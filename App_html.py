<!-- templates/login.html -->
<!-- Purpose: Allows users to log in by entering their name. Used by the /login route. -->
<!DOCTYPE html>
<html>
<head>
  <title>Login</title>
</head>
<body>
  <h2>Login</h2>
  {% if error %}
    <p style="color: red;">{{ error }}</p>
  {% endif %}
  <form method="POST">
    <input type="text" name="name" placeholder="Enter your name" required><br><br>
    <button type="submit">Login</button>
  </form>
  <p>Don't have an account? <a href="/register">Register here</a></p>
</body>
</html>

<!-- templates/register.html -->
<!-- Purpose: Allows users to register by entering their name and selecting if they are an admin. Used by the /register route. -->
<!DOCTYPE html>
<html>
<head>
  <title>Register</title>
</head>
<body>
  <h2>Register</h2>
  {% if error %}
    <p style="color: red;">{{ error }}</p>
  {% endif %}
  <form method="POST">
    <input type="text" name="name" placeholder="Enter your name" required><br><br>
    <label><input type="checkbox" name="is_admin"> Is Admin?</label><br><br>
    <button type="submit">Register</button>
  </form>
  <p>Already registered? <a href="/login">Login here</a></p>
</body>
</html>

<!-- templates/dashboard.html -->
<!-- Purpose: Displays the user's dashboard with links to savings, loan, and repayments. Admins see an additional link to the admin dashboard. Used by the /dashboard route. -->
<!DOCTYPE html>
<html>
<head>
  <title>Dashboard</title>
</head>
<body>
  <h2>Welcome, {{ name }}!</h2>
  <a href="/savings">View Savings</a><br>
  <a href="/loan">Apply for Loan</a><br>
  <a href="/repayments">View Repayments</a><br>
  {% if is_admin %}
    <a href="/admin">Admin Dashboard</a><br>
  {% endif %}
  <a href="/logout">Logout</a>
</body>
</html>

<!-- templates/savings.html -->
<!-- Purpose: Displays the user's savings history and total savings. Used by the /savings route. -->
<!DOCTYPE html>
<html>
<head>
  <title>Savings</title>
</head>
<body>
  <h2>Savings History</h2>
  <p>Total Savings: ₦{{ total }}</p>
  {% if not savings %}
    <p>No savings recorded.</p>
  {% else %}
    <table border="1">
      <tr><th>Amount</th><th>Date</th></tr>
      {% for amount, date in savings %}
        <tr><td>₦{{ amount }}</td><td>{{ date }}</td></tr>
      {% endfor %}
    </table>
  {% endif %}
  <a href="/dashboard">Back</a>
</body>
</html>

<!-- templates/loan.html -->
<!-- Purpose: Allows users to apply for a loan by filling out a detailed form and displays their pending loan applications. Used by the /loan route. -->
<!DOCTYPE html>
<html>
<head>
  <title>Loan</title>
</head>
<body>
  <h2>Loan History</h2>
  <table border="1">
    <tr><th>Type of Loan</th><th>Amount</th><th>Duration</th><th>Date</th><th>Status</th></tr>
    {% for app in applications %}
      <tr>
        <td>{{ app[2] }}</td><td>₦{{ app[3] }}</td><td>{{ app[4] }} months</td><td>{{ app[20] }}</td><td>{{ app[21] }}</td>
      </tr>
    {% endfor %}
  </table>
  <h3>Apply for a Loan</h3>
  {% if error %}
    <p style="color: red;">{{ error }}</p>
  {% endif %}
  <form method="POST">
    <input type="text" name="type_of_loan" placeholder="Type of Loan" required><br>
    <input type="number" name="amount" placeholder="Loan Amount" step="0.01" required><br>
    <input type="number" name="duration" placeholder="Repayment Duration (months)" required><br>
    <input type="text" name="ecn_staff_no" placeholder="ECN Staff No" required><br>
    <input type="text" name="ippis_no" placeholder="IPPIS No" required><br>
    <input type="text" name="designation" placeholder="Designation" required><br>
    <input type="text" name="phone_no" placeholder="Phone No" required><br>
    <input type="text" name="bank_name" placeholder="Bank Name" required><br>
    <input type="text" name="account_no" placeholder="Account No" required><br>
    <input type="number" name="previous_month_salary" placeholder="Previous Month Salary (₦)" step="0.01" required><br>
    <h4>Guarantor 1</h4>
    <input type="text" name="guarantor1_name" placeholder="Name" required><br>
    <input type="text" name="guarantor1_staff_no" placeholder="Staff No" required><br>
    <input type="text" name="guarantor1_designation" placeholder="Designation" required><br>
    <input type="text" name="guarantor1_phone_no" placeholder="Phone No" required><br>
    <h4>Guarantor 2</h4>
    <input type="text" name="guarantor2_name" placeholder="Name" required><br>
    <input type="text" name="guarantor2_staff_no" placeholder="Staff No" required><br>
    <input type="text" name="guarantor2_designation" placeholder="Designation" required><br>
    <input type="text" name="guarantor2_phone_no" placeholder="Phone No" required><br>
    <label><input type="checkbox" name="deduct_interest" value="YES"> Deduct Interest from Amount Loaned?</label><br>
    <input type="number" name="monthly_equity_contribution" placeholder="Monthly Equity Contribution (₦)" step="0.01" required><br>
    <button type="submit">Submit</button>
  </form>
  <a href="/dashboard">Back</a>
</body>
</html>

<!-- templates/repayments.html -->
<!-- Purpose: Displays the user's repayment schedule with options to mark repayments as paid. Used by the /repayments route. -->
<!DOCTYPE html>
<html>
<head>
  <title>Repayments</title>
</head>
<body>
  <h2>Repayment Schedule</h2>
  {% if error %}
    <p>{{ error }}</p>
  {% else %}
    <table border="1">
      <tr><th>Due Date</th><th>Amount</th><th>Status</th><th>Action</th></tr>
      {% for repayment_id, due, amount, status in repayments %}
        <tr>
          <td>{{ due }}</td>
          <td>₦{{ amount }}</td>
          <td>{{ 'Unpaid' if status == 0 else 'Paid' }}</td>
          <td>
            {% if status == 0 %}
              <a href="/mark_paid/{{ repayment_id }}">Mark as Paid</a>
            {% endif %}
          </td>
        </tr>
      {% endfor %}
    </table>
  {% endif %}
  <a href="/dashboard">Back</a>
</body>
</html>

<!-- templates/admin.html -->
<!-- Purpose: Displays the admin dashboard with links to manage savings, users, and loan approvals. Used by the /admin route. -->
<!DOCTYPE html>
<html>
<head>
  <title>Admin Dashboard</title>
</head>
<body>
  <h2>Admin Dashboard</h2>
  <a href="/add_savings">Add Savings</a><br>
  <a href="/users">View Users</a><br>
  <a href="/approve_loans">Approve Loans</a><br>
  <a href="/dashboard">Back</a>
</body>
</html>

<!-- templates/add_savings.html -->
<!-- Purpose: Allows admins to add savings for users by selecting a staff member and entering an amount. Used by the /add_savings route. -->
<!DOCTYPE html>
<html>
<head>
  <title>Add Savings</title>
</head>
<body>
  <h2>Add Savings</h2>
  {% if error %}
    <p style="color: red;">{{ error }}</p>
  {% endif %}
  <form method="POST">
    <select name="staff_id" required>
      {% for user in users %}
        <option value="{{ user[0] }}">{{ user[1] }}</option>
      {% endfor %}
    </select>
    <input type="number" name="amount" placeholder="Amount" required>
    <button type="submit">Add</button>
  </form>
  <a href="/admin">Back</a>
</body>
</html>

<!-- templates/users.html -->
<!-- Purpose: Displays a list of all users in the system for admins to view. Used by the /users route. -->
<!DOCTYPE html>
<html>
<head>
  <title>Users</title>
</head>
<body>
  <h2>Users</h2>
  <table border="1">
    <tr><th>ID</th><th>Name</th></tr>
    {% for user in users %}
      <tr><td>{{ user[0] }}</td><td>{{ user[1] }}</td></tr>
    {% endfor %}
  </table>
  <a href="/admin">Back</a>
</body>
</html>

<!-- templates/approve_loans.html -->
<!-- Purpose: Displays a list of pending loan applications for admins to approve or edit approval details. Used by the /approve_loans route. -->
<!DOCTYPE html>
<html>
<head>
  <title>Approve Loans</title>
</head>
<body>
  <h2>Loan Requests</h2>
  <table border="1">
    <tr><th>Loan ID</th><th>Staff Name</th><th>Amount</th><th>Action</th></tr>
    {% for app in applications %}
      <tr>
        <td>{{ app[0] }}</td><td>{{ app[3] }}</td><td>₦{{ app[2] }}</td>
        <td><a href="/approve/{{ app[0] }}">Approve</a> | <a href="/loan_approval_details/{{ app[0] }}">Edit Details</a></td>
      </tr>
    {% endfor %}
  </table>
  <a href="/admin">Back</a>
</body>
</html>

<!-- templates/loan_approval_details.html -->
<!-- Purpose: Allows admins to edit the "For Official Use Only" section of a loan (amount approved, interest, total amount). Used by the /loan_approval_details route. -->
<!DOCTYPE html>
<html>
<head>
  <title>Loan Approval Details</title>
</head>
<body>
  <h2>Loan Approval Details</h2>
  {% if loan %}
    <form method="POST">
      <p>Type of Loan: {{ loan[2] }}</p>
      <p>Amount Requested: ₦{{ loan[3] }}</p>
      <div><label>Amount Approved (₦): <input type="number" name="amount_approved" value="{{ loan[15] or loan[3] }}" step="0.01" required></label></div>
      <div><label>Interest Charged (₦): <input type="number" name="interest_charged" value="{{ loan[16] or 0 }}" step="0.01" required></label></div>
      <div><label>Total Amount (₦): <input type="number" name="total_amount" value="{{ loan[17] or loan[3] }}" step="0.01" required></label></div>
      <button type="submit">Update</button>
    </form>
  {% else %}
    <p>No loan details found.</p>
  {% endif %}
  <a href="/approve_loans">Back</a>
</body>
</html>
