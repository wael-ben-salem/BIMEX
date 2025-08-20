# Script de test pour vérifier la configuration unifiée
Write-Host "=== TEST DE LA CONFIGURATION UNIFIÉE ===" -ForegroundColor Magenta

# Test 1: Vérifier que le backend démarre
Write-Host "`n1. Test du backend intégré..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/" -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Backend principal accessible" -ForegroundColor Green
    } else {
        Write-Host "✗ Backend principal non accessible" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Backend principal non accessible: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Vérifier que l'API OCR est disponible
Write-Host "`n2. Test de l'API OCR..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/ocr/" -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ API OCR accessible" -ForegroundColor Green
    } else {
        Write-Host "✗ API OCR non accessible" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ API OCR non accessible: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Vérifier que le frontend unifié est accessible
Write-Host "`n3. Test du frontend unifié..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080/" -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Frontend unifié accessible" -ForegroundColor Green
    } else {
        Write-Host "✗ Frontend unifié non accessible" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Frontend unifié non accessible: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Vérifier que l'interface intégrée est accessible
Write-Host "`n4. Test de l'interface intégrée..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080/app/index-integrated.html" -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Interface intégrée accessible" -ForegroundColor Green
    } else {
        Write-Host "✗ Interface intégrée non accessible" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Interface intégrée non accessible: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Vérifier que le XeoKit viewer est accessible
Write-Host "`n5. Test du XeoKit viewer..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080/app/index.html" -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ XeoKit viewer accessible" -ForegroundColor Green
    } else {
        Write-Host "✗ XeoKit viewer non accessible" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ XeoKit viewer non accessible: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 6: Vérifier que l'OCR frontend React est accessible
Write-Host "`n6. Test de l'OCR frontend React..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/" -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ OCR frontend React accessible" -ForegroundColor Green
    } else {
        Write-Host "✗ OCR frontend React non accessible" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ OCR frontend React non accessible: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== RÉSUMÉ DE LA CONFIGURATION UNIFIÉE ===" -ForegroundColor Cyan
Write-Host "Backend intégré:     http://localhost:8001" -ForegroundColor White
Write-Host "Frontend unifié:     http://localhost:8080" -ForegroundColor White
Write-Host "OCR Frontend React:  http://localhost:3000" -ForegroundColor White
Write-Host "`n=== LIENS RAPIDES ===" -ForegroundColor Yellow
Write-Host "🎯 Interface principale: http://localhost:8080" -ForegroundColor White
Write-Host "📱 Interface intégrée:   http://localhost:8080/app/index-integrated.html" -ForegroundColor White
Write-Host "🏗️ XeoKit Viewer:        http://localhost:8080/app/index.html" -ForegroundColor White
Write-Host "📷 OCR React:            http://localhost:3000" -ForegroundColor White
Write-Host "`nPour démarrer tous les services, utilisez: .\start-all-unified.ps1" -ForegroundColor Yellow

