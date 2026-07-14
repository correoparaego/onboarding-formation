import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import es from "./es.json";

// Spanish is the default UI language (proposal: Spanish UI; i18n scaffold).
i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      es: { translation: es },
    },
    fallbackLng: "es",
    lng: "es",
    interpolation: { escapeValue: false },
  });

export default i18n;
