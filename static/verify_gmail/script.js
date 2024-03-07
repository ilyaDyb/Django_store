// const codes = document.querySelectorAll('.code');

// codes.forEach((code, idx) => {
//     // code.addEventListener('input', (e) => {
//     //     const inputValue = e.target.value;
        
//     //     if (inputValue.length === 1 && !isNaN(inputValue)) {
//     //         setTimeout(() => codes[idx + 1]?.focus(), 10);
//     //     } else if (inputValue.length > 1) {
//     //         code.value = inputValue[0]; // Оставить только первую цифру
//     //     }
//     // });

//     code.addEventListener('keydown', (e) => {
//         if (e.key === 'Backspace' && !code.value) {
//             setTimeout(() => codes[idx - 1]?.focus(), 10);
//         }
//     });
// });

// codes[0].focus();