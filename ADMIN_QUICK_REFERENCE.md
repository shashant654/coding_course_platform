# Quick Reference Guide - Payment Verification & Daily Classes

## Admin Dashboard Quick Links

### 🛒 Payment Management
**URL:** `/admin/payments/`

#### Payment Configuration
- **URL:** `/admin/payments/paymentconfig/`
- **Purpose:** Configure UPI QR code and Razorpay keys
- **Steps:**
  1. Click on "Payment Config"
  2. Upload UPI QR code image
  3. Enter UPI ID (e.g., `yourname@bankname`)
  4. Enter Razorpay keys (if using)
  5. Save

#### Payment Transactions
- **URL:** `/admin/payments/paymenttransaction/`
- **Purpose:** Verify and approve/reject student payments
- **Quick Actions:**
  1. Click filter by "Status" → "Pending"
  2. Review pending transactions
  3. Click transaction to view screenshot
  4. Compare UTR with submitted form
  5. Select transaction(s)
  6. Choose action: "Approve selected payments" or "Reject selected payments"
  7. Click "Go"

#### Orders
- **URL:** `/admin/payments/order/`
- **Purpose:** View all orders and their status
- **Information Displayed:**
  - Order number
  - User who placed order
  - Amount and discount
  - Payment status
  - Who verified (admin user)
  - When verified

---

### 📅 Daily Classes Management
**URL:** `/admin/enrollment/`

#### Creating a New Daily Class
1. Go to `/admin/enrollment/dailyclass/`
2. Click "Add Daily Class"
3. Fill in the form:

| Field | Example | Notes |
|-------|---------|-------|
| Title | "React Hooks Deep Dive" | Topic/class name |
| Description | "In this session we'll..." | Agenda and learning points |
| Course | Select course | Leave blank for all students |
| Date | Today | Pick date |
| Scheduled Time | 14:30 | 24-hour format |
| Duration (minutes) | 60 | How long class will be |
| Meet Link | https://meet.google.com/abc-defg-hij | Google Meet URL |
| Is Active | ✓ Checked | Check to make visible |

4. Click "Save"

**Result:**
- Class appears in student's "Daily Classes" page
- If today: appears under "Today's Classes" with "Join Now" button
- If future: appears under "Upcoming Classes"
- Auto-populated: `created_by` (current admin), timestamps

#### Editing Existing Class
1. Go to `/admin/enrollment/dailyclass/`
2. Click on the class to edit
3. Modify fields
4. Click "Save"

#### Hiding/Unpublishing Class
1. Go to the class
2. Uncheck "Is Active"
3. Click "Save"
4. Class no longer visible to students

#### Viewing Student Eligibility
- **General Classes:** Visible to all enrolled students
- **Course-Specific Classes:** Only visible to students enrolled in that course

---

## Payment Verification Process

### Step-by-Step Verification

#### 1. Locate Pending Payments
```
/admin/payments/paymenttransaction/
↓
Filter by Status: "Pending"
↓
View list of pending transactions
```

#### 2. Review Payment Details
```
Click on transaction
↓
View Order information:
  - Order number
  - User details
  - Amount
  - Order date
↓
View Transaction information:
  - UTR number submitted
  - Payment method
  - Amount
  - Date/time submitted
↓
View Payment Screenshot:
  - Click or scroll to see screenshot preview
  - Verify:
    ✓ Transaction date matches
    ✓ UTR number visible
    ✓ Amount matches order amount
    ✓ UPI ID matches (if applicable)
```

#### 3. Make Decision

**APPROVE if:**
- ✓ UTR is valid and matches format
- ✓ Amount matches order total
- ✓ Screenshot shows authentic transaction
- ✓ UPI ID matches configured ID
- ✓ No duplicate payment already approved

**Steps to Approve:**
1. Check transaction details
2. Go back to transaction list
3. Select the transaction checkbox
4. Select "Approve selected payments" from Actions dropdown
5. Click "Go"
6. Confirmation message appears
7. Student receives approval email

**REJECT if:**
- ✗ UTR format invalid
- ✗ Amount doesn't match
- ✗ Screenshot looks suspicious or doctored
- ✗ Same UTR submitted multiple times (only approve first)
- ✗ UPI ID doesn't match configured ID
- ✗ Transaction status is unclear

**Steps to Reject:**
1. Go to Order admin
2. Find corresponding order
3. Enter rejection reason in "Rejection Reason" field
4. Go to Payment Transaction
5. Select transaction
6. Select "Reject selected payments" from Actions dropdown
7. Click "Go"
8. Student receives rejection email with reason
9. Student can resubmit with different UTR

---

## Key Admin Pages Reference

### Core Admin Links
| Page | URL | Purpose |
|------|-----|---------|
| Dashboard | `/admin/` | Admin home |
| Payments | `/admin/payments/` | Payment section |
| Transactions | `/admin/payments/paymenttransaction/` | Verify payments |
| Orders | `/admin/payments/order/` | View orders |
| Daily Classes | `/admin/enrollment/dailyclass/` | Create classes |
| Enrollments | `/admin/enrollment/enrollment/` | View enrollments |

---

## Common Scenarios & Solutions

### Scenario 1: Payment Screenshot is Blurry
**Problem:** Can't read UTR or amount in screenshot

**Solution:**
1. Ask student to resubmit with clearer screenshot
2. Reject transaction with reason: "Screenshot unclear, please resubmit"
3. Student receives rejection email
4. Student can resubmit with better quality

**Rejection reason to use:**
```
"Payment screenshot quality is too low. Please resubmit with a clear screenshot showing the UTR, amount, and timestamp."
```

### Scenario 2: UTR Number Doesn't Match
**Problem:** UTR in screenshot doesn't match form submission

**Solution:**
1. Reject transaction
2. Reason: "UTR number in screenshot doesn't match submitted UTR"
3. Student corrects and resubmits

### Scenario 3: Amount Mismatch
**Problem:** Amount in screenshot is different from order amount

**Solution:**
1. Reject transaction
2. Reason: "Payment amount doesn't match order amount. Please check and resubmit."

**Details to check:**
- Order amount: Check in Order admin
- Submitted amount: Check in Payment Transaction
- Screenshot amount: Compare in preview

### Scenario 4: Duplicate Payment
**Problem:** Same student submitted same UTR multiple times

**Solution:**
1. Approve ONLY the first transaction
2. Reject subsequent ones
3. Reason: "Duplicate payment detected. First submission already approved."

### Scenario 5: Class Too Few Interested Students
**Problem:** Created class but no students joining

**Solution:**
1. Edit class to make it more general (remove course filter)
   OR
2. Send announcement to specific course
   OR
3. Mark as inactive if class doesn't serve current needs

---

## Email Notifications - What Students Receive

### When Payment Approved
```
Subject: Payment Approved - ORD-ABC1234567

✓ Order approved message
✓ Order details with amount
✓ List of enrolled courses
✓ Link to "Go to My Learning"
✓ Courses now accessible
```

**When:** Immediately after admin clicks "Approve"

### When Payment Rejected
```
Subject: Payment Verification Issue - ORD-ABC1234567

✗ Verification failed message
✗ Order details
✗ Rejection reason (if provided)
✗ Troubleshooting tips
✗ Contact support link
```

**When:** Immediately after admin clicks "Reject"

---

## Data Security Notes

### Payment Screenshots
- Stored in: `/media/payment/screenshots/`
- Access: Admin only (in admin interface)
- Retention: Keep for record (2+ years recommended)
- Sensitive: Contains UPI ID and transaction details

### Payment Information
- All transactions logged and timestamped
- Admin who verified recorded in database
- Rejection reasons tracked
- Audit trail available

### Best Practices
1. Only approve payments you're confident about
2. Log rejection reason for records
3. Double-check UTR matches before approving
4. Don't approve duplicate payments
5. Ask for clarification if unsure

---

## Frequently Asked Questions

### Q: How long to approve payments?
**A:** Within 24 hours is standard. Set expectations accordingly.

### Q: What if screenshot looks fake?
**A:** Reject it. Better safe than sorry. Ask student to provide proof or contact support.

### Q: Can I undo an approval?
**A:** Not directly. Contact developer to revert if needed.

### Q: Can I delete a transaction?
**A:** Not recommended. Disable in database if absolutely necessary.

### Q: How to handle very high amounts?
**A:** Add extra verification. Ask for proof of payment or contact support.

### Q: What if student disputes payment?
**A:** Check transaction records and screenshot. If legitimate, approve. Otherwise, maintain rejection.

### Q: Can I set auto-approval?
**A:** Not currently. Manual verification provides security.

### Q: How to train new admins?
**A:** Share this document + supervise first 10 approvals.

---

## Daily Operations Checklist

### Daily (Before Classes)
- [ ] Check "Today's Classes" are active and have correct meet links
- [ ] Verify no technical issues with Google Meet links

### 2-3 Times Daily
- [ ] Check pending payment transactions
- [ ] Approve valid payments
- [ ] Reject suspicious payments
- [ ] Update rejection reasons

### Weekly
- [ ] Review payment trends
- [ ] Check daily class attendance
- [ ] Schedule next week's classes
- [ ] Clean up inactive classes

### Monthly
- [ ] Generate payment report
- [ ] Verify all approvals were legitimate
- [ ] Update payment configuration if needed
- [ ] Plan upcoming classes

---

## Support Contacts

**For Technical Issues:**
- Check `/admin/payments/` error messages
- Review Django error logs
- Contact development team

**For Student Issues:**
- Check student's order history
- View their enrollments
- Review their payment transaction details

---

**Last Updated:** December 1, 2025
**Version:** 1.0
**Status:** Ready for Production Use
