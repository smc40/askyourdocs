export default {
    backendUrl: process.env.BACKEND_URL || document.location.origin,
    easterEggTrigger: 'magic schnauz',
    easterEggTriggerMsg: 'magic schnauz 〰️',
};

console.log(
    `Backend URL: ${process.env.BACKEND_URL || document.location.origin}`
);

console.log(`document.location.origin: ${document.location.origin}`);
