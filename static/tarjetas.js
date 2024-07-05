document.addEventListener("DOMContentLoaded", () => {
    const resultDiv = document.getElementById('results');
    document.getElementById("cardForm").addEventListener("submit", async (event) => {
        event.preventDefault();
        resultDiv.innerHTML = '';

        const cardNumber = document.getElementById("card_number").value;
        //console.log("A: " +cardNumber);

        try {
            const response = await fetch('/validate_card', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'card_number': cardNumber
                })
            });
            console.log("Response: " +response);
            const data = await response.json();
            console.log("Data: " +data);
            
            if (data.success && data.BIN && data.BIN.country) {
                const binInfo = data.BIN;
                const pais = data.BIN.country.native;
                const moneda = data.BIN.country.currency;
                console.log(`Pais: ${pais}`);

                resultDiv.innerHTML = `
                    <h2>Detalles de la tarjeta</h2>
                    <p>Valid: ${binInfo.valid}</p>
                    <p>Tipo: ${binInfo.scheme}</p>
                    <p>Pais: ${pais}</p>
                    <p>Moneda: ${moneda}</p>
                `
            }
            else {
                console.log(data);
                resultDiv.innerHTML = `<p>Se produjo un error</p>`;
            }
        } catch (error) {
            console.error("El error fue: " + error);

            document.getElementById('results').innerHTML = `<p> ${error.message} </p>`;
        }
    });
    // Código para el formato de Expiration MM/AA
    document.getElementById('typeExp').addEventListener('input', function (e) {
        let input = e.target.value.replace(/\D/g, '').substring(0, 4); // Obtener solo los primeros 4 dígitos
        let month = input.substring(0, 2);
        let year = input.substring(2, 4);

        if (input.length > 2) {
            e.target.value = `${month}/${year}`;
        } else if (input.length === 0) {
            e.target.value = '';
        } else {
            e.target.value = `${month}`;
        }
    });
});

