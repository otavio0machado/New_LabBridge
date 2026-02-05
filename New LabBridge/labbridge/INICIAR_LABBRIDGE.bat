@echo off
title LabBridge - Sistema de Auditoria Laboratorial
color 0A

echo.
echo  ========================================
echo       LABBRIDGE - Iniciando Servidor
echo  ========================================
echo.
echo  Aguarde enquanto o sistema inicia...
echo  O navegador abrira automaticamente.
echo.
echo  Para FECHAR: Pressione Ctrl+C ou feche esta janela
echo.
echo  ----------------------------------------

cd /d "%~dp0"

:: Abre o navegador após 10 segundos
start /b cmd /c "timeout /t 10 /nobreak >nul && start http://localhost:3000"

:: Inicia o Reflex
reflex run

pause
