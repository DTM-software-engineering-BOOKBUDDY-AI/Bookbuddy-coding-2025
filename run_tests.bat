@echo off
echo Running BookBuddy Test Suite
echo ==========================

if "%1"=="" (
    echo Running all tests...
    python -m pytest
) else if "%1"=="verbose" (
    echo Running tests with verbose output...
    python -m pytest -v
) else if "%1"=="coverage" (
    echo Running tests with coverage report...
    python -m pytest --cov=Bookbuddy_app
) else if "%1"=="full" (
    echo Running tests with verbose output and coverage report...
    python -m pytest -v --cov=Bookbuddy_app
) else (
    echo Running specific test module: %1
    python -m pytest %1 -v
)

echo.
echo Test run complete!
echo.
echo Usage:
echo   run_tests.bat         - Run all tests
echo   run_tests.bat verbose - Run all tests with verbose output
echo   run_tests.bat coverage - Run all tests with coverage report
echo   run_tests.bat full     - Run tests with verbose output and coverage
echo   run_tests.bat [path]   - Run specific test module
echo. 