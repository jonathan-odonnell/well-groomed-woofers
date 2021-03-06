let stripePublicKey = $("#id_stripe_public_key").text().slice(1, -1);
let clientSecret = $("#id_client_secret").text().slice(1, -1);
let stripe = Stripe(stripePublicKey);
let elements = stripe.elements();
let style = {
    base: {
        color: "#000",
        fontFamily: '"Source Sans Pro", sans-serif',
        fontSmoothing: "antialiased",
        fontSize: "16px",
        "::placeholder": {
            color: "#aab7c4",
        },
    },
    invalid: {
        color: "#dc3545",
        iconColor: "#dc3545",
    },
};
let card = elements.create("card", {
    style: style
});
card.mount("#card-element");

// Handle realtime validation errors on the card element
card.addEventListener("change", function (event) {
    let errorDiv = document.getElementById("card-errors");
    if (event.error) {
        let html = `
                <span class="icon" role="alert">
                    <i class="fas fa-times"></i>
                </span>
                <span>${event.error.message}</span>
            `;
        $(errorDiv).html(html);
    } else {
        errorDiv.textContent = "";
    }
});

// Handle form submit
let form = document.getElementById("payment-form");

form.addEventListener("submit", function (e) {
    e.preventDefault();
    card.update({
        disabled: true
    });
    $("#submit-button").attr("disabled", true);

    let saveInfo = $("#id-save-info").is(":checked")
    let csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
    let postData = {
        csrfmiddlewaretoken: csrfToken,
        client_secret: clientSecret,
        save_info: saveInfo,
    };
    let url = "/checkout/cache-checkout-data/";

    $.post(url, postData).done(function () {
        stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: card,
                billing_details: {
                    name: $.trim(form.full_name.value),
                    phone: $.trim(form.phone_number.value),
                    email: $.trim(form.email.value),
                    address: {
                        line1: $.trim(form.address_line_1.value),
                        line2: $.trim(form.address_line_2.value),
                        city: $.trim(form.town_or_city.value),
                        state: $.trim(form.county.value),
                        country: $.trim(form.country.value),
                        postal_code: $.trim(form.postcode.value),
                    },
                },
            },
            shipping: {
                name: $.trim(form.full_name.value),
                phone: $.trim(form.phone_number.value),
                address: {
                    line1: $.trim(form.address_line_1.value),
                    line2: $.trim(form.address_line_2.value),
                    city: $.trim(form.town_or_city.value),
                    state: $.trim(form.county.value),
                    country: $.trim(form.country.value),
                    postal_code: $.trim(form.postcode.value),
                },
            },
        }).then(function (result) {
            console.log(result)
            if (result.error) {
                let errorDiv = document.getElementById("card-errors");
                let html = `
                    <span class="icon" role="alert">
                    <i class="fas fa-times"></i>
                    </span>
                    <span>${result.error.message}</span>`;
                $(errorDiv).html(html);
                $("#payment-form").fadeToggle(100);
                card.update({
                    disabled: false
                });
                $("#submit-button").attr("disabled", false);
            } else {
                if (result.paymentIntent.status === "succeeded") {
                    form.submit();
                }
            }
        })
    }).fail(function () {
        // Reload the page, the error will be in django messages
        location.reload();
    });
});