import globals from "globals";
import pluginReact from "eslint-plugin-react";
import pluginReactHooks from "eslint-plugin-react-hooks";

/** @type {import('eslint').Linter.Config} */
const config = {
  overrides: [
    {
      files: ["**/*.{js,jsx,ts,tsx}"],
      languageOptions: {
        globals: globals.browser,
      },
      plugins: ["react", "react-hooks"],
      extends: [
        "plugin:react/recommended",
        "plugin:react-hooks/recommended",
        "eslint:recommended"
      ],
      rules: {
        "react/react-in-jsx-scope": "off", // React 17+ doesn't require this rule
        "react/prop-types": "off", // Optional: If you don't want to enforce prop types
        "react-hooks/rules-of-hooks": "error", // Enforce the rules of hooks
        "react-hooks/exhaustive-deps": "warn", // Warn about missing dependencies in effect hooks
      },
    },
  ],
};

export default config;
