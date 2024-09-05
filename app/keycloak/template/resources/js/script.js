var passwordFields = [
    {
        input: "password",
        toggler: "password-toggle-button",
        hidden: true
    }, 
    {
        input: "password-new",
        toggler: "password-new-toggle-button",
        hidden: true
    }, 
    {
        input: "password-confirm",
        toggler: "password-confirm-toggle-button",
        hidden: true
    }
];

document.addEventListener('DOMContentLoaded', (event) => {
    passwordFields.forEach(element => {
        let passwordToggle = document.getElementById(element.toggler);
        if(passwordToggle) {
            passwordToggle.addEventListener("click", (e) => {
                let passwordInput = document.getElementById(element.input);
                if(element.hidden) {
                    passwordInput.setAttribute("type", "text");
                    passwordToggle.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true" role="presentation" xmlns="http://www.w3.org/2000/svg"><path d="M12 6c3.79 0 7.17 2.13 8.82 5.5-.59 1.22-1.42 2.27-2.41 3.12l1.41 1.41c1.39-1.23 2.49-2.77 3.18-4.53C21.27 7.11 17 4 12 4c-1.27 0-2.49.2-3.64.57l1.65 1.65C10.66 6.09 11.32 6 12 6zm-1.07 1.14L13 9.21c.57.25 1.03.71 1.28 1.28l2.07 2.07c.08-.34.14-.7.14-1.07C16.5 9.01 14.48 7 12 7c-.37 0-.72.05-1.07.14zM2.01 3.87l2.68 2.68C3.06 7.83 1.77 9.53 1 11.5 2.73 15.89 7 19 12 19c1.52 0 2.98-.29 4.32-.82l3.42 3.42 1.41-1.41L3.42 2.45 2.01 3.87zm7.5 7.5l2.61 2.61c-.04.01-.08.02-.12.02-1.38 0-2.5-1.12-2.5-2.5 0-.05.01-.08.01-.13zm-3.4-3.4l1.75 1.75c-.23.55-.36 1.15-.36 1.78 0 2.48 2.02 4.5 4.5 4.5.63 0 1.23-.13 1.77-.36l.98.98c-.88.24-1.8.38-2.75.38-3.79 0-7.17-2.13-8.82-5.5.7-1.43 1.72-2.61 2.93-3.53z" fill="#9E9E9E"/></svg>';
                } else {
                    passwordInput.setAttribute("type", "password");
                    passwordToggle.innerHTML = '<svg width="20" height="14" viewBox="0 0 20 14" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M19.525 5.76663C17.3249 3.34163 13.6916 0.766632 9.99995 0.833299C6.30828 0.899965 2.67495 3.34163 0.474951 5.76663C0.16224 6.10782 -0.0112305 6.55382 -0.0112305 7.01663C-0.0112305 7.47945 0.16224 7.92545 0.474951 8.26663C1.94162 9.84997 5.61662 13.1666 9.99995 13.1666C14.3833 13.1666 18.0499 9.8333 19.525 8.22497C19.826 7.88631 19.9923 7.44893 19.9923 6.9958C19.9923 6.54267 19.826 6.10529 19.525 5.76663ZM6.16662 6.99997C6.16662 6.24181 6.39144 5.50067 6.81265 4.87028C7.23386 4.23989 7.83255 3.74856 8.533 3.45843C9.23345 3.16829 10.0042 3.09238 10.7478 3.24029C11.4914 3.3882 12.1744 3.75329 12.7105 4.28939C13.2466 4.82549 13.6117 5.50853 13.7596 6.25212C13.9075 6.99571 13.8316 7.76647 13.5415 8.46692C13.2514 9.16737 12.76 9.76606 12.1296 10.1873C11.4992 10.6085 10.7581 10.8333 9.99995 10.8333C8.98329 10.8333 8.00826 10.4294 7.28937 9.71054C6.57049 8.99165 6.16662 8.01663 6.16662 6.99997Z" fill="#9E9E9E"/><path d="M9.99992 8.66658C10.9204 8.66658 11.6666 7.92039 11.6666 6.99992C11.6666 6.07944 10.9204 5.33325 9.99992 5.33325C9.07944 5.33325 8.33325 6.07944 8.33325 6.99992C8.33325 7.92039 9.07944 8.66658 9.99992 8.66658Z" fill="#9E9E9E"/></svg>';
                }
                element.hidden = !element.hidden;
            });
        }
    });
    lightIcon = document.querySelector('link#light-favicon');
    darkIcon = document.querySelector('link#dark-favicon');
    matcher = window.matchMedia('(prefers-color-scheme: dark)');

    if (matcher.matches) {
      darkIcon.remove();
      document.head.append(lightIcon);
    } else {
      document.head.append(darkIcon);
      lightIcon.remove();
    }
});