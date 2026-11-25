
// Format currency in Pakistani Rupees
function formatCurrency(value) {
    return "Rs. " + Number(value).toLocaleString("en-PK", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Load calculation history from MongoDB
function loadHistory() {
    $.ajax({
        url: "/api/history",
        method: "GET",
        success: function(records) {

            const table = $("#historyTable");
            table.empty();

            if (records.length === 0) {
                table.append(`
                    <tr>
                        <td colspan="5" class="text-center">
                            No calculations found.
                        </td>
                    </tr>
                `);
                return;
            }

            records.forEach(function(record) {
                table.append(`
                    <tr>
                        <td>${formatCurrency(record.principal)}</td>
                        <td>${record.rate}%</td>
                        <td>${record.months}</td>
                        <td>${formatCurrency(record.emi)}</td>
                        <td>${record.servedBy}</td>
                    </tr>
                `);
            });
        },

        error: function() {
            $("#historyTable").html(`
                <tr>
                    <td colspan="5" class="text-danger text-center">
                        Unable to load history.
                    </td>
                </tr>
            `);
        }
    });
}

// Submit EMI calculation form
$("#emiForm").on("submit", function(event) {

    // Prevent normal page refresh
    event.preventDefault();

    const P = Number($("#loanAmount").val());
    const rate = Number($("#interestRate").val());
    const n = Number($("#tenure").val());

    // Client-side validation
    if (
        !Number.isFinite(P) ||
        !Number.isFinite(rate) ||
        !Number.isInteger(n) ||
        P <= 0 ||
        rate <= 0 ||
        n <= 0
    ) {
        $("#errorMessage")
            .removeClass("d-none")
            .text("Please enter positive values. Tenure must be a whole number.");

        return;
    }

    $("#errorMessage").addClass("d-none");

    // Send calculation request to backend
    $.ajax({
        url: "/api/emi",
        method: "POST",
        contentType: "application/json",

        data: JSON.stringify({
            P: P,
            rate: rate,
            n: n
        }),

        success: function(result) {

            // Display EMI results
            $("#emiResult").text(formatCurrency(result.emi));

            $("#totalPayment").text(
                formatCurrency(result.totalPayment)
            );

            $("#totalInterest").text(
                formatCurrency(result.totalInterest)
            );

            $("#servedBy").text(result.servedBy);
            $("#podIP").text(result.podIP);

            // Show result panel
            $("#resultPanel").removeClass("d-none");

            // Refresh history table
            loadHistory();
        },

        error: function(xhr) {

            const message = xhr.responseJSON?.error ||
                "Unable to calculate EMI. Please try again.";

            $("#errorMessage")
                .removeClass("d-none")
                .text(message);
        }
    });
});

// Load history when page opens
$(document).ready(function() {
    loadHistory();
});
