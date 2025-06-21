const { execSync } = require('child_process');
const path = require('path');
const os = require('os');
const fs = require('fs');

// Detectar sistema operativo
const isWindows = os.platform() === 'win32';

// Determinar rutas según el sistema operativo
const venvPath = isWindows ? '.venv\\Scripts' : '.venv/bin';
const pipPath = isWindows ? `${venvPath}\\pip` : `${venvPath}/pip`;
const pythonPath = isWindows ? `${venvPath}\\python` : `${venvPath}/python`;
const activateCmd = isWindows ? `${venvPath}\\activate` : `source ${venvPath}/activate`;

// Determinar si el entorno virtual existe
const venvExists = fs.existsSync(isWindows ? '.venv\\Scripts' : '.venv/bin');

// Determinar modo (dev o producción)
const isDev = process.argv.includes('--dev');

// No pasamos --debug como argumento al script
const flaskArgs = 'run.py';

try {
  // Verificar si el entorno virtual necesita ser creado o actualizado
  if (!venvExists) {
    console.log('🔧 Creando entorno virtual...');
    execSync(isWindows ? 'python -m venv .venv' : 'python3 -m venv .venv', { 
      stdio: 'inherit',
      shell: true 
    });
  }
  
  // Instalar o actualizar dependencias
  console.log('📦 Instalando dependencias...');
  const pipInstallCmd = isWindows
    ? `${pipPath} install -r requirements.txt`
    : `${pipPath} install -r requirements.txt`;
  
  execSync(pipInstallCmd, { 
    stdio: 'inherit',
    shell: true 
  });

  // Construir comando para ejecutar Flask
  const runCmd = isWindows
    ? `${pythonPath} ${flaskArgs}`
    : `${pythonPath} ${flaskArgs}`;
  
  console.log(`🚀 Iniciando servidor Flask: ${runCmd}`);
  
  // Ejecutar comando
  execSync(runCmd, { 
    stdio: 'inherit',
    shell: true,
    env: { 
      ...process.env, 
      PATH: `${path.resolve(venvPath)}${path.delimiter}${process.env.PATH}`,
      FLASK_APP: 'app.app',
      // En lugar de --debug, usamos las variables de entorno para configurar Flask
      FLASK_ENV: isDev ? 'development' : 'production',
      FLASK_DEBUG: isDev ? '1' : '0'  // Esto activa el modo debug de Flask
    }
  });
} catch (error) {
  console.error('❌ Error:', error.message);
  process.exit(1);
}