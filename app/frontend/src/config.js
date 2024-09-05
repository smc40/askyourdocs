export default {
    backendUrl: process.env.BACKEND_URL || document.location.origin,
    easterEggTrigger: 'magic schnauz',
    easterEggTriggerMsg: 'magic schnauz 〰️',
};

console.log(
    `Backend URL: ${process.env.BACKEND_URL || document.location.origin}`
);

console.log(`document.location.origin: ${document.location.origin}`);

// export default {
//     backendUrl: 'https://api.ayd-sandbox.4punkt0.ch', // Hardcoded URL
//     easterEggTrigger: 'magic schnauz',
//     easterEggTriggerMsg: 'magic schnauz 〰️',
// };

// console.log('Backend URL: https://api.ayd-sandbox.4punkt0.ch');

// console.log(`document.location.origin: ${document.location.origin}`);
