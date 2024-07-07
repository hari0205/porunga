examples = [
    {
        "diff": "diff --git a/app.py b/app.py\nindex f39ad2c..b3e2b44 100644\n--- a/app.py\n+++ b/app.py\n@@ -10,7 +10,7 @@\n def start():\n-    log('App started')\n+    logger.info('App has started')",
        "x": 3,
        "suggestions": """<suggestions>
        <message>[ref] Rename log to logger.info for consistency</message>
        <message>[fix] Improve log message clarity in start function</message>
        <message>[enhancement] Use logger.info instead of log for better logging</message>
    </suggestions>""",
    },
    {
        "diff": "diff --git a/main.py b/main.py\nindex a1c9f56..e5d3f89 100644\n--- a/main.py\n+++ b/main.py\n@@ -20,8 +20,8 @@\n def process_data(data):\n-    results = parse(data)\n-    save(results)\n+    parsed_data = parse(data)\n+    save_data(parsed_data)",
        "x": 2,
        "suggestions": """<suggestions>
        <message>[ref] Rename variable results to parsed_data</message>
        <message>[ref] Rename function save to save_data for clarity</message>
    </suggestions>""",
    },
    {
        "diff": "diff --git a/utils.py b/utils.py\nindex 2bfc89a..ff4b5e2 100644\n--- a/utils.py\n+++ b/utils.py\n@@ -5,5 +5,5 @@\n def calculate(a, b):\n-    return a + b\n+    return a - b",
        "x": 4,
        "suggestions": """<suggestions>
        <message>[fix] Correct calculation operation from addition to subtraction</message>
        <message>[ref] Update function logic in calculate</message>
        <message>[fix] Adjust calculation function to perform subtraction</message>
        <message>[enhancement] Improve accuracy of calculate function by correcting operation</message>
    </suggestions>""",
    },
]
