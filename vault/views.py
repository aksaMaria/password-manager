from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from cryptography.fernet import Fernet, InvalidToken

from .models import SavedPassword


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


def encrypt_password(plain):
    # settings.VAULT_ENCRYPTION_KEY must be a Fernet key.
    return Fernet(settings.VAULT_ENCRYPTION_KEY).encrypt(plain.encode()).decode()


@login_required
@require_POST
def save_password(request):
    website = request.POST.get("website", "").strip()
    username = request.POST.get("username", "").strip()
    password = request.POST.get("password", "")

    if not (website and username and password):
        messages.error(request, "Website, username, and password are required.")
        return redirect("home")

    SavedPassword.objects.create(
        user=request.user,
        website=website,
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
    entries = SavedPassword.objects.filter(user=request.user).order_by(
        "-is_favorite", "website"
    )
    return render(request, "my_vault.html", {"entries": entries})


@login_required
@require_POST
@never_cache
def reveal_password(request, pk):
    entry = get_object_or_404(SavedPassword, pk=pk, user=request.user)
    try:
        return JsonResponse({"password": decrypt_password(entry.encrypted_password)})
    except InvalidToken:
        return JsonResponse(
            {"error": "This password can't be read. The encryption key has changed."},
            status=400,
        )


@login_required
@require_POST
def delete_password(request, pk):
    entry = get_object_or_404(SavedPassword, pk=pk, user=request.user)
    website = entry.website
    entry.delete()
    messages.success(request, f"Deleted the password for {website}.")
    return redirect("vault_list")