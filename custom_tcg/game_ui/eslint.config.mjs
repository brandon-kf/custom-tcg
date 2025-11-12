// eslint.config.mjs
// @ts-check
import eslint from "@eslint/js"
import jsdoc from "eslint-plugin-jsdoc"
import { defineConfig } from "eslint/config"
import tseslint from "typescript-eslint"

export default defineConfig(
    eslint.configs.recommended, // ESLint's recommended rules
    ...tseslint.configs.recommendedTypeChecked, // TypeScript ESLint's recommended rules with type information
    ...tseslint.configs.stylisticTypeChecked, // TypeScript ESLint's stylistic rules with type information
    {
        languageOptions: {
            parserOptions: {
                project: true, // Enable typed linting
                // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
                tsconfigRootDir: import.meta.dirname, // Point to the root directory of your project
            },
        },
        plugins: { jsdoc },
        rules: {
            "@typescript-eslint/consistent-type-imports": "error",
            "jsdoc/require-jsdoc": [
                "warn",
                {
                    require: {
                        FunctionDeclaration: true,
                        MethodDefinition: true,
                        ClassDeclaration: true,
                    },
                },
            ],
            "jsdoc/require-description": "warn",
            // ... other JSDoc rules
        },
    },
)
