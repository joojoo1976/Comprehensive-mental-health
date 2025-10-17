@echo off
set JAVA_HOME=C:\Program Files\Java\jdk-17
set ANDROID_HOME=C:\Users\foryo\AppData\Local\Android\Sdk
set PATH=%JAVA_HOME%\bin;%ANDROID_HOME%\tools;%ANDROID_HOME%\platform-tools;%PATH%
set GRADLE_OPTS=-Dorg.gradle.daemon=false -Dorg.gradle.parallel=true
set JAVA_OPTS=-Xmx4096m -XX:+UseParallelGC
cd /d "%~dp0"
call gradlew.bat clean :app:assembleDebug --no-daemon --console=plain --stacktrace