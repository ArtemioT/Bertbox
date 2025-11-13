function buttonAction(name) {
            document.getElementById('output').innerText = `${name}`;
            console.log(`${name} was pressed`);
            // You can replace this with fetch('/your_api') if using Flask later
        }