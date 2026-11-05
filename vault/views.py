import time
from collections import Counter

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from cryptography.fernet import Fernet, InvalidToken

from .models import SavedPassword

from .utils import password_strength


def home(request):
    return render(request, "home.html")


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("register")

        User.objects.create_user(
            username=username,
            password=password
        )

        messages.success(request, "Account created! Please log in.")
        return redirect("login")

    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("home")

        messages.error(request, "Invalid username or password!")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("home")


MASTER_MAX_FAILS = 5      # wrong master-password tries allowed...
MASTER_WINDOW = 300       # ...within this many seconds
EDIT_UNLOCK_SECONDS = 300  # how long an unlocked edit page stays valid

_url_validator = URLValidator(schemes=["http", "https"])


def clean_url(raw):
    """Return a normalised http(s) URL, "" if blank, or None if invalid."""
    raw = (raw or "").strip()
    if not raw:
        return ""
    if "://" not in raw:
        raw = "https://" + raw
    try:
        _url_validator(raw)
    except ValidationError:
        return None
    return raw


def check_master_password(request):
    """Re-verify the signed-in user's login password.

    Returns None when it is correct, otherwise (message, http_status).
    Repeated failures are throttled per session.
    """
    now = time.time()
    fails = [t for t in request.session.get("master_fails", []) if now - t < MASTER_WINDOW]
    if len(fails) >= MASTER_MAX_FAILS:
        request.session["master_fails"] = fails
        return "Too many wrong attempts. Please wait a few minutes.", 429
    if request.user.check_password(request.POST.get("master_password", "")):
        request.session["master_fails"] = []
        return None
    fails.append(now)
    request.session["master_fails"] = fails
    return "Wrong master password.", 403


def encrypt_password(plain):
    # settings.VAULT_ENCRYPTION_KEY must be a Fernet key.
    return Fernet(settings.VAULT_ENCRYPTION_KEY).encrypt(plain.encode()).decode()


@login_required
@require_POST
def save_password(request):
    website = request.POST.get("website", "").strip()
    username = request.POST.get("username", "").strip()
    password = request.POST.get("password", "")
    url = clean_url(request.POST.get("url", ""))


    if not (website and username and password):
        messages.error(request, "Website, username, and password are required.")
        return redirect("home")
    if url is None:
        messages.error(request, "That site URL doesn't look valid.")
        return redirect("home")

    SavedPassword.objects.create(
        user=request.user,
        website=website,
        url=url,
        username=username,
        encrypted_password=encrypt_password(password),
        category=request.POST.get("category", "").strip() or "Other",

        username=username,
        encrypted_password=encrypt_password(password),
        category=request.POST.get("category", "").strip(),
        notes=request.POST.get("notes", "").strip(),
        is_favorite="is_favorite" in request.POST,
    )
    messages.success(request, f"Saved the password for {website}.")
    return redirect("home")


def decrypt_password(token):
    return Fernet(settings.VAULT_ENCRYPTION_KEY).decrypt(token.encode()).decode()


@login_required
def vault_list(request):
    entries = list(
        SavedPassword.objects.filter(user=request.user).order_by("-is_favorite", "website")
    )

    # Decrypt in memory only to work out reused/weak; plaintext never reaches the template.
    plain = {}
    for e in entries:
        try:
            plain[e.pk] = decrypt_password(e.encrypted_password)
        except InvalidToken:
            plain[e.pk] = None
    counts = Counter(p for p in plain.values() if p)
    for e in entries:
        p = plain[e.pk]
        e.is_reused = bool(p) and counts[p] > 1
        e.is_weak = bool(p) and password_strength(p) == "weak"

    summary = {
        "total": len(entries),
        "reused": sum(1 for e in entries if e.is_reused),
        "weak": sum(1 for e in entries if e.is_weak),
    }
    return render(request, "my_vault.html", {"entries": entries, "summary": summary})
    entries = SavedPassword.objects.filter(user=request.user).order_by(
        "-is_favorite", "website"
    )
    return render(request, "my_vault.html", {"entries": entries})


@login_required
@require_POST
@never_cache
def reveal_password(request, pk):
    entry = get_object_or_404(SavedPassword, pk=pk, user=request.user)
    problem = check_master_password(request)
    if problem:
        return JsonResponse({"error": problem[0]}, status=problem[1])
    try:
        return JsonResponse({"password": decrypt_password(entry.encrypted_password)})
    except InvalidToken:
        return JsonResponse(
            {"error": "This password can't be read. The encryption key has changed."},
            status=400,
        )


@login_required
@never_cache
def edit_password(request, pk):
    entry = get_object_or_404(SavedPassword, pk=pk, user=request.user)
    key = f"edit_unlock_{pk}"
    unlocked = time.time() - request.session.get(key, 0) < EDIT_UNLOCK_SECONDS
    action = request.POST.get("action")

    if request.method == "POST" and action == "unlock":
        problem = check_master_password(request)
        if problem:
            messages.error(request, problem[0])
        else:
            request.session[key] = time.time()
        return redirect("edit_password", pk=pk)

    if not unlocked:
        return render(request, "edit.html", {"entry": entry, "locked": True})

    if request.method == "POST" and action == "save":
        website = request.POST.get("website", "").strip()
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        url = clean_url(request.POST.get("url", ""))
        if not (website and username and password):
            messages.error(request, "Website, username, and password are required.")
            return redirect("edit_password", pk=pk)
        if url is None:
            messages.error(request, "That site URL doesn't look valid.")
            return redirect("edit_password", pk=pk)

        entry.website = website
        entry.url = url
        entry.username = username
        entry.encrypted_password = encrypt_password(password)
        entry.category = request.POST.get("category", "").strip() or "Other"
        entry.notes = request.POST.get("notes", "").strip()
        entry.is_favorite = "is_favorite" in request.POST
        entry.save()
        request.session.pop(key, None)
        messages.success(request, f"Updated {website}.")
        return redirect("vault_list")

    try:
        current = decrypt_password(entry.encrypted_password)
    except InvalidToken:
        current = ""
        messages.error(request, "The saved password can't be read (the encryption key changed). Enter a new one.")
    return render(request, "edit.html", {"entry": entry, "locked": False, "password": current})


@login_required
@require_POST
def toggle_favorite(request, pk):
    entry = get_object_or_404(SavedPassword, pk=pk, user=request.user)
    entry.is_favorite = not entry.is_favorite
    entry.save(update_fields=["is_favorite", "updated_at"])
    return redirect("vault_list")


@login_required
@require_POST
def delete_password(request, pk):
    entry = get_object_or_404(SavedPassword, pk=pk, user=request.user)
    website = entry.website
    entry.delete()
    messages.success(request, f"Deleted the password for {website}.")
    return redirect("vault_list")
