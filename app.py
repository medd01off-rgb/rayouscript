<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Calculator</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f0f2f5;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .card {
            background: #ffffff;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
            width: 320px;
            text-align: center;
        }
        h2 {
            margin-bottom: 10px;
            color: #1a73e8;
        }
        p {
            font-size: 14px;
            color: #666;
            margin-bottom: 20px;
        }
        input {
            width: 100%;
            padding: 12px;
            font-size: 18px;
            border: 2px solid #ddd;
            border-radius: 8px;
            box-sizing: border-box;
            text-align: center;
            outline: none;
            transition: border-color 0.3s;
        }
        input:focus {
            border-color: #1a73e8;
        }
        button {
            width: 100%;
            padding: 12px;
            margin-top: 15px;
            background-color: #1a73e8;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover {
            background-color: #1557b0;
        }
        .result-box {
            margin-top: 25px;
            padding: 15px;
            background-color: #e8f0fe;
            border-radius: 8px;
            display: none;
        }
        .result-title {
            font-size: 14px;
            color: #555;
        }
        .code {
            font-size: 32px;
            font-weight: bold;
            color: #1e8e3e;
            letter-spacing: 2px;
            margin-top: 5px;
        }
    </style>
</head>
<body>

<div class="card">
    <h2>Code Generator</h2>
    <p>Enter a decimal number (e.g., 34.7313)</p>
    
    <input type="text" id="numInput" placeholder="34.7313">
    <button onclick="calculateCode()">Generate Code</button>

    <div class="result-box" id="resultBox">
        <div class="result-title">Your Code:</div>
        <div class="code" id="codeResult">0000</div>
    </div>
</div>

<script>
function calculateCode() {
    const inputVal = document.getElementById('numInput').value.trim();
    const resultBox = document.getElementById('resultBox');
    const codeResult = document.getElementById('codeResult');

    if (!inputVal.includes('.')) {
        alert("Please enter a decimal number containing a dot (e.g., 34.7313).");
        return;
    }

    const parts = inputVal.split('.');
    const intPart = parts[0];  // Number before decimal (e.g., 34)
    const fracPart = parts[1]; // Number after decimal (e.g., 7313)

    if (isNaN(intPart) || isNaN(fracPart) || intPart === '' || fracPart === '') {
        alert("Please enter a valid decimal number.");
        return;
    }

    // 1. Construct multiplier: 48 + . + integer part (e.g., 48.34)
    const multiplier = parseFloat("48." + intPart);

    // 2. Convert fraction part to integer (e.g., 7313)
    const fracVal = parseInt(fracPart, 10);

    // 3. Calculation: 7313 * 48.34 = 353510.42
    const totalResult = fracVal * multiplier;

    // 4. Get integer part as string (353510)
    const resultIntStr = Math.floor(totalResult).toString();

    // 5. Extract last 4 digits (3510)
    const last4 = resultIntStr.padStart(4, '0').slice(-4);

    codeResult.innerText = last4;
    resultBox.style.display = "block";
}
</script>

</body>
</html>
