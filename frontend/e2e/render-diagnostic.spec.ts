import { test, expect } from '@playwright/test';

/**
 * Script de diagnóstico para verificar que Render está funcionando
 */

const BASE_URL = 'https://onboarding-formation.onrender.com';
const ADMIN_USER = 'admin';
const ADMIN_PASS = 'admin1234';

test.describe('Render Diagnostic Tests', () => {
  test('Verify Render is accessible', async ({ page }) => {
    console.log('🔍 Verificando que Render está accesible...');
    
    // Aumentar timeout para cold start
    test.setTimeout(120000);
    
    // Intentar cargar la página con reintentos
    let attempts = 0;
    const maxAttempts = 3;
    
    while (attempts < maxAttempts) {
      try {
        console.log(`Intento ${attempts + 1}/${maxAttempts}...`);
        await page.goto(BASE_URL, { 
          waitUntil: 'domcontentloaded',
          timeout: 60000 
        });
        
        // Esperar un poco para que React renderice
        await page.waitForTimeout(5000);
        
        // Tomar captura de lo que sea que haya cargado
        await page.screenshot({ 
          path: 'screenshots/render/diagnostic/00-initial-load.png',
          fullPage: true 
        });
        
        console.log('✅ Página cargada (o al menos intentó cargar)');
        console.log(`URL actual: ${page.url()}`);
        console.log(`Título: ${await page.title()}`);
        
        // Verificar si hay algún contenido
        const bodyText = await page.locator('body').textContent();
        console.log(`Contenido visible: ${bodyText?.substring(0, 200)}...`);
        
        break;
      } catch (error) {
        attempts++;
        console.log(`❌ Intento ${attempts} falló: ${error.message}`);
        if (attempts < maxAttempts) {
          console.log('Esperando 10 segundos antes de reintentar...');
          await page.waitForTimeout(10000);
        }
      }
    }
  });

  test('Test Admin Login Flow', async ({ page }) => {
    console.log('🔐 Probando flujo de login admin...');
    test.setTimeout(120000);
    
    // Navegar a login
    await page.goto(`${BASE_URL}/admin/login`, { 
      waitUntil: 'domcontentloaded',
      timeout: 60000 
    });
    
    await page.waitForTimeout(5000);
    
    // Capturar estado inicial
    await page.screenshot({ 
      path: 'screenshots/render/diagnostic/01-login-page.png',
      fullPage: true 
    });
    
    // Intentar login
    console.log('Intentando login...');
    await page.fill('input[type="text"], input[name="username"]', ADMIN_USER);
    await page.fill('input[type="password"]', ADMIN_PASS);
    
    await page.screenshot({ 
      path: 'screenshots/render/diagnostic/02-before-submit.png',
      fullPage: true 
    });
    
    // Click en submit
    await page.click('button[type="submit"]');
    
    // Esperar respuesta
    await page.waitForTimeout(10000);
    
    // Capturar resultado
    await page.screenshot({ 
      path: 'screenshots/render/diagnostic/03-after-submit.png',
      fullPage: true 
    });
    
    console.log(`URL después de login: ${page.url()}`);
  });
});
