document.addEventListener('DOMContentLoaded', function () {
    // Get all the tab panels and tab buttons
    const allTabs = document.querySelectorAll('.tab-panel');
    const allTabButtons = document.querySelectorAll('.tab-button');

    // Initially, hide all tabs
    allTabs.forEach(tab => {
        tab.style.display = 'none';  // Hide all tabs
    });

    // Initially, deactivate all tab buttons
    allTabButtons.forEach(button => {
        button.classList.remove('active');  // Remove 'active' class from all buttons
    });

    // Set the first tab button to be active on page load
    const firstTabButton = document.getElementById('sendPaymentTabBtn');
    firstTabButton.classList.add('active');  // Add 'active' class to the first tab button

    // Handle tab button clicks
    document.getElementById('sendPaymentTabBtn').addEventListener('click', function () {
        const sendTab = document.getElementById('sendPaymentTab');
        activateTab(sendTab, firstTabButton);
    });

    document.getElementById('trackPaymentTabBtn').addEventListener('click', function () {
        const trackTab = document.getElementById('trackPaymentTab');
        const trackButton = document.getElementById('trackPaymentTabBtn');
        activateTab(trackTab, trackButton);
    });

    document.getElementById('settingsTabBtn').addEventListener('click', function () {
        const settingsTab = document.getElementById('settingsTab');
        const settingsButton = document.getElementById('settingsTabBtn');
        activateTab(settingsTab, settingsButton);
    });

    // Function to handle tab switching
    function activateTab(tab, tabButton) {
        // Hide all tabs
        allTabs.forEach(t => t.style.display = 'none');

        // Deactivate all tab buttons
        allTabButtons.forEach(button => button.classList.remove('active'));

        // Show the selected tab
        tab.style.display = 'block';

        // Activate the selected tab button
        tabButton.classList.add('active');
    }

    // Handle sending payment link
    document.getElementById('sendPaymentLinkBtn').addEventListener('click', function () {
        const name = document.getElementById('nameInput').value;
        const description = document.getElementById('descriptionInput').value;
        const email = document.getElementById('emailInput').value;
        const amount = document.getElementById('amountInput').value;

        // Get API keys from localStorage
        const apiKey = localStorage.getItem('razorpayApiKey');
        const apiSecret = localStorage.getItem('razorpaySecretKey');

        // Validation for required fields
        if (!name || !description || !email || !amount || !apiKey || !apiSecret) {
            alert('Please fill in all fields and ensure API keys are set.');
            return;
        }

        // Construct the payload
        const payload = {
            api_key: apiKey,
            api_secret: apiSecret,
            description: description,
            customer_name: name,
            customer_email: email,
            amount: amount
        };

        // Show "Sending..." message
        const statusMessage = document.getElementById('statusMessage');
        statusMessage.innerHTML = `
            <div style="text-align: center; padding: 20px;">
                <div style="
                    border: 4px solid #f3f3f3;
                    border-top: 4px solid #0a5ecb;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    animation: spin 1s linear infinite;
                    margin: 10px auto;
                "></div>
                <p style="color: #666; margin-top: 10px;">Sending payment link...</p>
            </div>
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        `;

        // Send the payment link request to the API
        fetch('http://127.0.0.1:5000/api/send-payment-link', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        })
            .then(response => response.json())
            .then(data => {
            // Handle success
                if (data.status === 'success') {
                    statusMessage.innerHTML = `
                    <div style="text-align: center; padding: 10px;">
                        <span style="
                            background-color: #d1fae5;
                            color: #059669;
                            padding: 8px 16px;
                            border-radius: 20px;
                            font-size: 14px;
                            display: inline-block;
                        ">
                            Payment link sent successfully to ${email} for ₹${amount}
                        </span>
                    </div>`;
                } else {
                    statusMessage.innerHTML = `<p style="color: #dc3545; text-align: center;">Failed to send payment link: ${data.error || 'Unknown error'}</p>`;
                }
            })
            .catch(error => {
            // Handle error
                console.error('Error:', error);
                statusMessage.innerHTML = '<p style="color: #dc3545; text-align: center;">There was an error sending the payment link. Please try again.</p>';
            });
    });

    // Automatically fetch and display the payment links
    const paymentLinksContainer = document.getElementById('paymentLinksContainer');
    const apiKey = localStorage.getItem('razorpayApiKey');
    const apiSecret = localStorage.getItem('razorpaySecretKey');

    if (apiKey && apiSecret) {
        // Show loading spinner
        paymentLinksContainer.innerHTML = `
            <div style="text-align: center; padding: 20px;">
                <div style="
                    border: 4px solid #f3f3f3;
                    border-top: 4px solid #0a5ecb;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    animation: spin 1s linear infinite;
                    margin: 10px auto;
                "></div>
                <p style="color: #666; margin-top: 10px;">Loading payment links...</p>
            </div>
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        `;

        fetch('http://127.0.0.1:5000/api/track-payments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                api_key: apiKey,
                api_secret: apiSecret
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success' && data.payment_links.length > 0) {
                    paymentLinksContainer.innerHTML = `
                    <table class="payment-table">
                        <thead>
                            <tr>
                                <th>Customer</th>
                                <th>Amount</th>
                                <th>Status</th>
                                <th>Payment Link</th>
                            </tr>
                        </thead>
                        <tbody>
                        </tbody>
                    </table>
                `;

                    const tableBody = paymentLinksContainer.querySelector('tbody');

                    data.payment_links.forEach(link => {
                        const statusClass = getStatusClass(link.status);

                        const row = document.createElement('tr');
                        row.innerHTML = `
                        <td>
                            <div>
                                <strong>${link.customer_name || 'N/A'}</strong><br>
                                <small>${link.customer_email || 'N/A'}</small><br>
                                <small>${link.customer_contact || 'N/A'}</small><br>
                                <em>${link.description || ''}</em>
                            </div>
                        </td>
                        <td>₹${link.amount}</td>
                        <td><span class="status-badge ${statusClass}">${link.status}</span></td>
                        <td>
                            <button onclick="copyToClipboard('${link.short_url}')">Copy</button>
                            <a href="${link.short_url}" target="_blank">Open</a>
                        </td>
                    `;
                        tableBody.appendChild(row);
                    });
                } else {
                    paymentLinksContainer.innerHTML = '<p>No payment links found.</p>';
                }

            })
            .catch(error => {
                console.error('Error fetching payment links:', error);
                paymentLinksContainer.innerHTML = '<p>Error fetching payment links.</p>';
            });
    } else {
        paymentLinksContainer.innerHTML = '<p>Please set your API key and secret in Settings.</p>';
    }

    // Toggle settings form visibility
    document.getElementById('settingsBtn').addEventListener('click', function () {
        document.getElementById('settingsBtn').style.display = 'none';
        const settingsForm = document.getElementById('settingsForm');
        settingsForm.style.display = settingsForm.style.display === 'none' ? 'block' : 'none';
    });

    // Save settings
    document.getElementById('saveSettingsBtn').addEventListener('click', function () {
        const apiKey = document.getElementById('apiKey').value;
        const secretKey = document.getElementById('secretKey').value;

        // Check if both fields are filled out
        if (!apiKey || !secretKey) {
            alert('Please fill in both API Key and Secret Key.');
            return;
        }

        // Save to localStorage
        localStorage.setItem('razorpayApiKey', apiKey);
        localStorage.setItem('razorpaySecretKey', secretKey);

        alert('Settings saved!');
        document.getElementById('settingsForm').style.display = 'none';
        document.getElementById('settingsBtn').style.display = 'block';
    });

    // On page load, check if there are saved settings and populate the input fields
    const savedApiKey = localStorage.getItem('razorpayApiKey');
    const savedSecretKey = localStorage.getItem('razorpaySecretKey');

    if (savedApiKey) {
        document.getElementById('apiKey').value = savedApiKey;  // Set the API Key in the input field
    }
    if (savedSecretKey) {
        document.getElementById('secretKey').value = savedSecretKey;  // Set the Secret Key in the input field
    }

    // Function to get the correct status class based on the payment status
    function getStatusClass(status) {
        switch (status) {
        case 'paid':
            return 'paid';
        case 'created':
            return 'created';
        case 'failed':
            return 'failed';
        case 'cancelled':
            return 'cancelled';
        default:
            return '';
        }
    }
});
