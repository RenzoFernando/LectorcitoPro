import js from "@eslint/js";

export default [
    {
        ...js.configs.recommended,
        files: ["resources/js/**/*.js"],
        languageOptions: {
            ecmaVersion: "latest",
            sourceType: "script",
            globals: {
                document: "readonly",
                IntersectionObserver: "readonly",
                URL: "readonly",
                window: "readonly"
            }
        }
    }
];
