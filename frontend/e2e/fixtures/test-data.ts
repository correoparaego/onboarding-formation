export const TEST_DATA = {
  admin: {
    username: 'admin',
    password: 'admin1234',
  },
  courses: [
    { id: 1, title: 'Seguridad en el Trabajo' },
    { id: 5, title: 'Prevencion de Riesgos Laborales' },
    { id: 6, title: 'Gestion de Equipos' },
    { id: 4, title: 'Normativa ISO 9001' },
  ],
  employees: [
    { name: 'Juan Perez', position: 'Operario' },
    { name: 'Maria Garcia', position: 'Tecnico' },
    { name: 'Carlos Lopez', position: 'Operario' },
    { name: 'Ana Martinez', position: 'Supervisor' },
  ],
  tokens: {
    'Roberto Molina': 'fJAIuBGJCsDO36bzrFFrSK1VKNW41yP_q5j_UwXTCcA',
    'Isabel Navarro': 'Mp-7BgqNonPUUz8nm3u53ucPr436BCca1Fzsrq1ydKY',
  },
};

export function getEmployeeToken(): string {
  return process.env.EMPLOYEE_TEST_TOKEN || TEST_DATA.tokens['Roberto Molina'] || '';
}
