# ============================================================
#  INSTALLER.ps1 - Installation automatique Meli-Melo 973
#  Lance ce script UNE SEULE FOIS pour tout configurer.
# ============================================================

$ErrorActionPreference = "Stop"

function Write-Step { param($msg) Write-Host "" ; Write-Host ">> $msg" -ForegroundColor Cyan }
function Write-Ok   { param($msg) Write-Host "   OK : $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "   ATTENTION : $msg" -ForegroundColor Yellow }
function Write-Err  { param($msg) Write-Host "   ERREUR : $msg" -ForegroundColor Red }
function Ask        { param($prompt) Read-Host "   $prompt" }

Clear-Host
Write-Host "============================================================"
Write-Host "   Meli-Melo 973 - Installation automatique"
Write-Host "   Blog : melimelo973.blogspot.com -> Netlify"
Write-Host "============================================================"
Write-Host ""
Write-Host "   Ce script va :"
Write-Host "   1. Installer Git, Python et Hugo (si absents)"
Write-Host "   2. Creer le depot GitHub"
Write-Host "   3. Creer le site Netlify"
Write-Host "   4. Configurer la synchronisation automatique"
Write-Host "   5. Importer tous vos poemes"
Write-Host ""
Write-Host "   Duree estimee : 5 a 10 minutes"
Write-Host ""
Ask "Appuyez sur ENTREE pour commencer (ou Ctrl+C pour annuler)"

# ============================================================
#  ETAPE 1 - Installation des outils
# ============================================================
Write-Step "ETAPE 1/6 - Verification et installation des outils"

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Warn "winget non disponible. Installez les outils manuellement :"
    Write-Host "   - Git    : https://git-scm.com/download/win"
    Write-Host "   - Python : https://www.python.org/downloads/"
    Write-Host "   - Hugo   : https://gohugo.io/installation/windows/"
    Ask "Une fois installes, appuyez sur ENTREE pour continuer"
} else {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Host "   Installation de Git..." -ForegroundColor Gray
        winget install --id Git.Git -e --source winget --silent
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        Write-Ok "Git installe"
    } else {
        Write-Ok "Git deja installe"
    }

    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Host "   Installation de Python..." -ForegroundColor Gray
        winget install --id Python.Python.3.11 -e --source winget --silent
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        Write-Ok "Python installe"
    } else {
        Write-Ok "Python deja installe"
    }

    if (-not (Get-Command hugo -ErrorAction SilentlyContinue)) {
        Write-Host "   Installation de Hugo..." -ForegroundColor Gray
        winget install --id Hugo.Hugo.Extended -e --source winget --silent
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        Write-Ok "Hugo installe"
    } else {
        Write-Ok "Hugo deja installe"
    }
}

Write-Host "   Installation des modules Python..." -ForegroundColor Gray
python -m pip install --quiet --upgrade requests html2text
Write-Ok "Modules Python installes"

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "   Installation de GitHub CLI..." -ForegroundColor Gray
    winget install --id GitHub.cli -e --source winget --silent
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    Write-Ok "GitHub CLI installe"
} else {
    Write-Ok "GitHub CLI deja installe"
}

# ============================================================
#  ETAPE 2 - Connexion GitHub
# ============================================================
Write-Step "ETAPE 2/6 - Connexion a GitHub"
Write-Host ""
Write-Host "   Vous allez etre redirige vers GitHub pour vous connecter."
Write-Host "   Si vous n'avez pas de compte, creez-en un sur https://github.com"
Write-Host ""
Ask "Appuyez sur ENTREE pour ouvrir le navigateur"

gh auth login --web --git-protocol https
if ($LASTEXITCODE -ne 0) {
    Write-Err "Echec de la connexion GitHub"
    exit 1
}

$githubUser = gh api user --jq ".login"
Write-Ok "Connecte en tant que : $githubUser"

# ============================================================
#  ETAPE 3 - Creation du depot GitHub
# ============================================================
Write-Step "ETAPE 3/6 - Creation du depot GitHub"

$repoName = "melimelo973-site"
$repoCheck = gh repo list $githubUser --json name --jq ".[].name" 2>$null | Select-String $repoName

if ($repoCheck) {
    Write-Warn "Le depot '$repoName' existe deja - on l'utilise"
} else {
    gh repo create "$githubUser/$repoName" --public --description "Site de poesie Meli-Melo 973"
    Write-Ok "Depot cree : https://github.com/$githubUser/$repoName"
}

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectDir

if (-not (Test-Path ".git")) {
    git init
    git add .
    git commit -m "Initial commit - Meli-Melo 973"
    git branch -M main
    git remote add origin "https://github.com/$githubUser/$repoName.git"
} else {
    git add .
    $diff = git diff --staged --name-only
    if ($diff) {
        git commit -m "Mise a jour"
    }
    $remoteExists = git remote 2>$null | Select-String "origin"
    if (-not $remoteExists) {
        git remote add origin "https://github.com/$githubUser/$repoName.git"
    }
}

git push -u origin main --force
Write-Ok "Code envoye sur GitHub"

# ============================================================
#  ETAPE 4 - Configuration Netlify
# ============================================================
Write-Step "ETAPE 4/6 - Configuration de Netlify"
Write-Host ""
Write-Host "   Vous avez besoin d'un compte Netlify (gratuit)."
Write-Host "   Ouvrez : https://app.netlify.com"
Write-Host ""
Write-Host "   Etape A - Creer le site :"
Write-Host "   1. Cliquez 'Add new site' -> 'Deploy manually'"
Write-Host "   2. Glissez n'importe quel dossier vide pour creer le site"
Write-Host "   3. Notez le Site ID (format : xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)"
Write-Host ""
Write-Host "   Etape B - Creer un token :"
Write-Host "   1. Cliquez sur votre avatar en haut a droite -> User settings"
Write-Host "   2. Allez dans Applications -> Personal access tokens"
Write-Host "   3. Cliquez 'New access token', nommez-le 'github-actions'"
Write-Host "   4. Copiez le token affiche (commence par nf_...)"
Write-Host ""

Start-Process "https://app.netlify.com"
Start-Sleep -Seconds 2

$netlifyToken  = Ask "Collez votre token Netlify (nf_...)"
$netlifySiteId = Ask "Collez votre Site ID Netlify"

if (-not $netlifyToken -or -not $netlifySiteId) {
    Write-Err "Token ou Site ID manquant. Relancez le script."
    exit 1
}

Write-Ok "Informations Netlify enregistrees"

# ============================================================
#  ETAPE 5 - Ajout des secrets GitHub
# ============================================================
Write-Step "ETAPE 5/6 - Configuration des secrets GitHub Actions"

$bloggerKey = "AIzaSyAlZcoFvzlr7KaMzyfL4L6vYEvMj2QQLyE"

gh secret set BLOGGER_API_KEY    --body $bloggerKey    --repo "$githubUser/$repoName"
gh secret set NETLIFY_AUTH_TOKEN --body $netlifyToken  --repo "$githubUser/$repoName"
gh secret set NETLIFY_SITE_ID    --body $netlifySiteId --repo "$githubUser/$repoName"

Write-Ok "3 secrets configures dans GitHub"

# ============================================================
#  ETAPE 6 - Premier import
# ============================================================
Write-Step "ETAPE 6/6 - Premier import de vos poemes"
Write-Host ""
Write-Host "   Lancement du workflow GitHub Actions..." -ForegroundColor Gray

gh workflow run sync.yml --repo "$githubUser/$repoName" -f force_reimport=true
Start-Sleep -Seconds 3

Write-Host "   Suivi de l'execution (patientez environ 2 minutes)..." -ForegroundColor Gray
gh run watch --repo "$githubUser/$repoName"

# ============================================================
#  FIN
# ============================================================
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "   Installation terminee avec succes !" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "   Votre site  : https://app.netlify.com/sites"
Write-Host "   Depot       : https://github.com/$githubUser/$repoName"
Write-Host "   Actions     : https://github.com/$githubUser/$repoName/actions"
Write-Host ""
Write-Host "   La synchronisation se fait automatiquement chaque nuit."
Write-Host "   Pour forcer une synchro : GitHub -> Actions -> Run workflow"
Write-Host ""
Ask "Appuyez sur ENTREE pour ouvrir votre site Netlify"
Start-Process "https://app.netlify.com/sites"
