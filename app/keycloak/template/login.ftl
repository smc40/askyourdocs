<#import "template.ftl" as layout>
<@layout.registrationLayout displayMessage=true; section>
  <#if section = "title">
      DORI - Login
  <#elseif section = "form">
      <form id="kc-form-login" action="${url.loginAction}" method="post">
            <div class="form-control">
                <label>Email</label>
                <input class="input" type="text" name="username" value="">
            </div>
            <div class="form-control">
                <label>Password</label>
                <span class="password">
                    <input class="input" type="password" id="password" name="password" value="">
                    <span class="icon" id="password-toggle-button">
                        <svg width="20" height="14" viewBox="0 0 20 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M19.525 5.76663C17.3249 3.34163 13.6916 0.766632 9.99995 0.833299C6.30828 0.899965 2.67495 3.34163 0.474951 5.76663C0.16224 6.10782 -0.0112305 6.55382 -0.0112305 7.01663C-0.0112305 7.47945 0.16224 7.92545 0.474951 8.26663C1.94162 9.84997 5.61662 13.1666 9.99995 13.1666C14.3833 13.1666 18.0499 9.8333 19.525 8.22497C19.826 7.88631 19.9923 7.44893 19.9923 6.9958C19.9923 6.54267 19.826 6.10529 19.525 5.76663ZM6.16662 6.99997C6.16662 6.24181 6.39144 5.50067 6.81265 4.87028C7.23386 4.23989 7.83255 3.74856 8.533 3.45843C9.23345 3.16829 10.0042 3.09238 10.7478 3.24029C11.4914 3.3882 12.1744 3.75329 12.7105 4.28939C13.2466 4.82549 13.6117 5.50853 13.7596 6.25212C13.9075 6.99571 13.8316 7.76647 13.5415 8.46692C13.2514 9.16737 12.76 9.76606 12.1296 10.1873C11.4992 10.6085 10.7581 10.8333 9.99995 10.8333C8.98329 10.8333 8.00826 10.4294 7.28937 9.71054C6.57049 8.99165 6.16662 8.01663 6.16662 6.99997Z" fill="#9E9E9E"/>
                        <path d="M9.99992 8.66658C10.9204 8.66658 11.6666 7.92039 11.6666 6.99992C11.6666 6.07944 10.9204 5.33325 9.99992 5.33325C9.07944 5.33325 8.33325 6.07944 8.33325 6.99992C8.33325 7.92039 9.07944 8.66658 9.99992 8.66658Z" fill="#9E9E9E"/>
                        </svg>
                    </span>
                </span>
            </div>
            <#if message?has_content>
                <#if message.type = 'error'>
                    <div class="error-message">
                        <p>${message.summary}</p>
                    </div>
                </#if>
            </#if>
            <button class="form-submit" type="submit">Login</button>
            <#if realm.resetPasswordAllowed>
                <a href="${url.loginResetCredentialsUrl}" class="password-reset">Forgot password ?</a>
            </#if>
      </form>
  </#if>
</@layout.registrationLayout>