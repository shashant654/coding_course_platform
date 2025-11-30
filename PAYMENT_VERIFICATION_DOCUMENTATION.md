# Payment Verification & Daily Classes Implementation Documentation

## Table of Contents
1. [Payment Verification Workflow](#payment-verification-workflow)
2. [Daily Classes Feature](#daily-classes-feature)
3. [Admin Interface](#admin-interface)
4. [Email Notifications](#email-notifications)
5. [User Experience](#user-experience)
6. [Testing Guide](#testing-guide)

---

## Payment Verification Workflow

### Overview
The payment verification system handles UPI payments and Razorpay payments with a verification workflow that includes:
- Payment submission by users
- Admin verification of manual payments
- Automatic enrollment upon approval
- Email notifications to users

### Payment Flow

#### 1. User Initiates Payment
- User adds courses to cart
- User proceeds to checkout
- User selects UPI payment method
- User is redirected to `/payments/payment/upi/`

#### 2. UPI Payment Page (`/payments/payment/upi/`)
The UPI payment page displays:
- **Scan QR Code Section:**
  - QR code image (configured in admin)
  - UPI ID for manual transfer (configured in admin)
  - Amount to pay

- **Submit Payment Details Section:**
  - Transaction Reference/UTR Number field (required)
  - Payment Screenshot upload (optional)
  - Submit button

**Form Submission (POST Request):**
- User enters 12-digit UTR number from payment confirmation
- User optionally uploads payment screenshot
- System creates:
  - `Order` object with `payment_status='pending'`
  - `OrderItem` objects for each course
  - `PaymentTransaction` object for verification tracking
- User is redirected to payment success page

#### 3. Payment Success Page (`/payments/payment_success/<order_number>/`)
Shows:
- Order confirmation message
- Order number and reference
- Payment status: **Pending Verification**
- Order details and items
- What happens next steps
- Important notes

#### 4. Admin Payment Verification
**Admin Interface:** `/admin/payments/paymenttransaction/`

Features:
- List all payment transactions
- Filter by:
  - Status (pending, success, failed)
  - Payment method
  - Date range
- Search by:
  - Transaction ID
  - Razorpay Order/Payment IDs
  - UPI Transaction Reference
  - Username or email

**Payment Verification Actions:**

a) **Verify Payment Screenshot:**
- Click on transaction to view details
- Full-size screenshot preview in admin detail view
- Thumbnail in list view (clickable)
- Compare with provided UTR number

b) **Approve Payment (Action):**
```
Steps:
1. Select transaction(s) with status 'pending'
2. Choose "Approve selected payments" from Actions dropdown
3. Click "Go"
```

Result:
- PaymentTransaction status → 'success'
- Order payment_status → 'completed'
- Order verified_by → Current admin user
- Order verified_at → Current timestamp
- Enrollments created automatically
- Course total_enrollments incremented
- Approval email sent to user

c) **Reject Payment (Action):**
```
Steps:
1. Select transaction(s) with status 'pending'
2. Choose "Reject selected payments" from Actions dropdown
3. Optionally enter rejection reason in Order admin
4. Click "Go"
```

Result:
- PaymentTransaction status → 'failed'
- Order payment_status → 'failed'
- Order verified_by → Current admin user
- Order verified_at → Current timestamp
- Order rejection_reason populated (if provided)
- Rejection email sent to user
- User can try payment again

### Database Schema

#### Order Model
```python
class Order(models.Model):
    user = ForeignKey(User)
    order_number = CharField (unique, auto-generated)
    total_amount = DecimalField
    discount_amount = DecimalField
    final_amount = DecimalField
    payment_status = CharField (choices: pending, completed, failed, refunded)
    payment_method = CharField (upi, razorpay, card)
    transaction_id = CharField
    razorpay_payment_id = CharField
    razorpay_order_id = CharField
    verified_by = ForeignKey(User, null=True)  # Admin who verified
    verified_at = DateTimeField (null=True)
    rejection_reason = TextField
    created_at = DateTimeField (auto_generated)
    updated_at = DateTimeField (auto_updated)
```

#### PaymentTransaction Model
```python
class PaymentTransaction(models.Model):
    order = ForeignKey(Order)
    transaction_id = CharField (unique)
    payment_method = CharField
    amount = DecimalField
    status = CharField (choices: pending, success, failed)
    razorpay_order_id = CharField
    razorpay_payment_id = CharField
    razorpay_signature = CharField
    upi_transaction_ref = CharField
    payment_screenshot = ImageField
    created_at = DateTimeField
    updated_at = DateTimeField
```

### Email Notifications

#### Payment Approved Email
**Trigger:** When admin clicks "Approve selected payments"

**Content:**
- Subject: "Payment Approved - {order_number}"
- User greeting
- Order details (number, amount, status)
- List of enrolled courses
- Link to My Learning page
- Call to action

**Template:** `payments/emails.py` - `send_payment_approved_email()`

#### Payment Rejected Email
**Trigger:** When admin clicks "Reject selected payments"

**Content:**
- Subject: "Payment Verification Issue - {order_number}"
- User greeting
- Order details
- Rejection reason (if provided)
- Troubleshooting steps
- Support contact information

**Template:** `payments/emails.py` - `send_payment_rejected_email()`

---

## Daily Classes Feature

### Overview
Daily Classes enable instructors to conduct live Google Meet sessions with enrolled students. Classes can be:
- **Course-specific:** Only visible to students enrolled in that course
- **General:** Visible to all enrolled students

### Models

#### DailyClass Model
```python
class DailyClass(models.Model):
    date = DateField  # Class date
    course = ForeignKey(Course, null=True)  # Leave blank for all students
    title = CharField  # Class title/topic
    description = TextField  # Agenda and topics
    meet_link = URLField  # Google Meet link
    scheduled_time = TimeField  # Start time
    duration_minutes = PositiveIntegerField (default=60)
    is_active = BooleanField (default=True)  # Show/hide class
    created_by = ForeignKey(User)  # Instructor
    created_at = DateTimeField (auto_generated)
    updated_at = DateTimeField (auto_updated)
```

### Admin Interface

**Access:** `/admin/enrollment/dailyclass/`

**Features:**
- Create/Edit daily classes
- Schedule date and time
- Assign to specific course or all students
- Upload/manage Google Meet links
- Publish/unpublish classes

**Field Organization:**
- Class Information: title, description, course
- Schedule: date, time, duration
- Meeting Details: meet_link
- Settings: is_active toggle
- Metadata: created_by, timestamps (readonly)

**Automatic Setup:**
- `created_by` field auto-populated with current admin user on creation
- Ordered by date descending, then time descending

### User Interface

#### Daily Classes Page (`/enrollment/daily-classes/`)

**Access:** Login required, must be enrolled in at least one course

**Sections:**

1. **Today's Classes**
   - Yellow/Warning header badge
   - Immediate join button
   - Direct link to Google Meet
   - Live indicator

2. **Upcoming Classes (Next 7 Days)**
   - Blue/Primary header
   - Full date and time display
   - "Link available at scheduled time" note
   - Calendar view preparation

3. **Past Classes (Last 3 Days)**
   - Gray/Secondary header
   - Faded appearance (opacity-75)
   - Reference indicator
   - Recording availability note

**Display Information:**
- Class title
- Course name (if course-specific)
- Date and time
- Duration
- Instructor name
- Description preview (15 words truncated)

**Filters Applied:**
- Only active classes (`is_active=True`)
- Only classes user is eligible for:
  - General classes (no course specified)
  - Course-specific classes for enrolled courses
- Automatically ordered by date and time

### Workflow

#### For Instructors

1. **Create Class:**
   - Go to Admin Dashboard
   - Navigate to Daily Classes
   - Click "Add Daily Class"
   - Fill in:
     - Title: "React Hooks Advanced Concepts"
     - Description: "Deep dive into custom hooks..."
     - Course: Select course (optional for all students)
     - Date: Select date
     - Time: Set start time
     - Duration: Set minutes
     - Google Meet Link: Paste link
   - Save

2. **Schedule:**
   - Class becomes visible to students 1 day before
   - "Link available at scheduled time" shown for upcoming
   - Can edit/update until class time

3. **Conduct Class:**
   - Share screen and teach
   - Students join via link

4. **Post-Class:**
   - Upload recording to course
   - Class appears in "Past Classes" for reference

#### For Students

1. **Browse Classes:**
   - Log in and go to "My Learning"
   - Click "Daily Classes" button

2. **Join Class:**
   - Click "Join Meet Now" for today's classes
   - Get redirected to Google Meet

3. **View Schedule:**
   - See upcoming classes
   - Note down dates and times
   - Set calendar reminders

### Visibility Logic

```python
enrolled_courses = Enrollment.objects.filter(user=user).values_list('course_id')

# Get classes
classes = DailyClass.objects.filter(
    is_active=True,
    date=target_date,  # Today, upcoming, or past
    Q(course=None) |  # General classes OR
    Q(course_id__in=enrolled_courses)  # Enrolled course classes
)
```

---

## Admin Interface

### Payment Configuration

**Access:** `/admin/payments/paymentconfig/`

**Settings:**
1. **UPI Configuration:**
   - Upload UPI QR Code image
   - Enter UPI ID (e.g., `yourname@bankname`)

2. **Razorpay Configuration:**
   - Razorpay Key ID
   - Razorpay Key Secret
   - Toggle test mode

### Payment Transaction Admin

**Columns in List View:**
- Transaction ID
- User (from order)
- Order reference
- Payment method
- Amount
- Status
- Screenshot thumbnail (clickable)
- Created date

**Filters:**
- Status (pending, success, failed)
- Payment method
- Date range

**Actions:**
- ✅ Approve selected payments
- ❌ Reject selected payments

**Detail View Features:**
- Full payment screenshot preview
- All transaction details
- Razorpay details (collapsed)
- UPI details and screenshot
- Timestamps

---

## Email Notifications

### Configuration

**Settings Required (settings.py):**
```python
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # or your SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'

# Site URL for email links
SITE_URL = 'http://localhost:8000'  # or your domain
```

### Approval Email

**Trigger:** Admin approves payment

**Example Email Content:**
```
Subject: Payment Approved - ORD-ABC1234567X

Dear John Doe,

Great news! Your payment has been verified and approved.

Order Details
─────────────
Order Number: ORD-ABC1234567X
Amount Paid: ₹999.00
Payment Status: Completed ✓

Enrolled Courses
─────────────
• React - The Complete Guide 2024
• JavaScript Advanced Concepts
• Web Development Masterclass

You can now access your enrolled courses from your learning dashboard.
[Go to My Learning Button]

Happy Learning!

---
If you have any questions, please contact our support team.
This is an automated email, please do not reply directly.
```

### Rejection Email

**Trigger:** Admin rejects payment

**Example Email Content:**
```
Subject: Payment Verification Issue - ORD-ABC1234567X

Dear John Doe,

We were unable to verify your payment for the following order:

Order Details
─────────────
Order Number: ORD-ABC1234567X
Amount: ₹999.00
Status: Verification Failed ✗

Reason
──────
[Admin-provided reason, e.g., "UTR number doesn't match payment amount"]

What to do next?
────────────────
• Check if your payment was actually deducted from your account
• Keep your payment screenshot/transaction ID ready
• Contact support with your order number: ORD-ABC1234567X

[Contact Support Button]

We apologize for any inconvenience.

---
Support Email: support@codelearn.com
This is an automated email, please do not reply directly.
```

---

## User Experience

### My Learning Page (`/enrollment/my-learning/`)

**Updated Features:**
1. **Enhanced Stats:**
   - Total Courses (enrolled count)
   - Completed (completed count)
   - In Progress (total - completed)

2. **Quick Access:**
   - Daily Classes button
   - Wishlist button

3. **Course Cards:**
   - Course thumbnail
   - Instructor name
   - Progress bar with percentage
   - Status badge (In Progress / Completed)
   - Continue Learning button
   - Enrollment date

4. **Empty State:**
   - "No enrolled courses yet" message
   - Browse Courses button

### Payment Success Flow

1. **User submits UPI payment form**
2. **Order created with pending status**
3. **User sees success page with:**
   - ✅ Submission confirmation
   - ⏳ "Pending Verification" status
   - 📝 Order details
   - 📚 Courses in order
   - 🔔 What happens next information
   - 📋 Important notes

4. **Within 24 hours:**
   - Admin verifies payment
   - System approves payment
   - Automatic enrollments created

5. **User receives:**
   - Email approval notification
   - Can immediately access courses
   - User visits My Learning page
   - Courses now appear with full access

---

## Testing Guide

### 1. UPI Payment Flow

**Test Steps:**
1. Log in as student
2. Add multiple courses to cart
3. Proceed to checkout
4. Select UPI payment
5. Enter 12-digit UTR number (e.g., 123456789012)
6. Optionally upload screenshot
7. Submit form

**Expected Results:**
- Order created with pending status ✓
- PaymentTransaction created ✓
- User redirected to success page ✓
- Success message shown ✓
- Courses not yet accessible ✓

### 2. Admin Payment Verification

**Test Steps:**
1. Log in as admin
2. Go to Payments → Payment Transactions
3. Find the pending transaction
4. Click to view details
5. Verify screenshot and UTR
6. Select transaction
7. Choose "Approve selected payments"
8. Click "Go"

**Expected Results:**
- Transaction status → success ✓
- Order payment_status → completed ✓
- Order verified_by → Current admin ✓
- verified_at populated ✓
- Student automatically enrolled ✓
- Email sent to student ✓

### 3. Enrollment After Approval

**Test Steps:**
1. Log in as student after approval
2. Go to My Learning page
3. Verify courses appear

**Expected Results:**
- Courses now visible ✓
- Can click "Continue Learning" ✓
- Can access course player ✓

### 4. Daily Classes

**Test Steps (As Admin):**
1. Go to Enrollment → Daily Classes
2. Click "Add Daily Class"
3. Fill in details:
   - Title: "Live Q&A Session"
   - Course: Select a course
   - Date: Today
   - Time: Current or future time
   - Duration: 60
   - Meet Link: https://meet.google.com/abc-defg-hij
4. Save

**Test Steps (As Student):**
1. Log in as enrolled student
2. Go to My Learning
3. Click "Daily Classes"
4. Verify class appears in "Today's Classes" or "Upcoming"
5. Click "Join Meet Now"

**Expected Results:**
- Class visible to enrolled students ✓
- Class not visible to non-enrolled students ✓
- Google Meet link opens ✓
- Correct time and date displayed ✓

### 5. Email Notifications

**Approval Email Test:**
1. Approve a pending payment
2. Check student's email inbox
3. Verify email contains:
   - Order number ✓
   - Amount ✓
   - Course list ✓
   - "Go to My Learning" link ✓

**Rejection Email Test:**
1. Reject a pending payment with reason
2. Check student's email inbox
3. Verify email contains:
   - Order number ✓
   - Rejection reason ✓
   - Support instructions ✓

### 6. Edge Cases

**Test Case 1: Multiple Courses in Single Order**
- Add 3+ courses
- Submit UPI payment
- Verify all courses in order
- Verify all enrollments created on approval

**Test Case 2: Applied Coupon**
- Apply coupon before UPI payment
- Verify discount amount in order
- Verify final amount reflects discount

**Test Case 3: Duplicate Payment Rejection**
- Submit same UTR twice
- Reject second one
- Verify user can submit different UTR

**Test Case 4: Course-Specific Daily Class**
- Create class for Course A
- Enroll Student 1 in Course A only
- Enroll Student 2 in Course B only
- Verify class visible to Student 1 only

**Test Case 5: General Daily Class**
- Create class without assigning to course
- Enroll any students
- Verify class visible to all enrolled students

---

## Troubleshooting

### Issue: Emails not sending
**Solution:**
- Check Django settings email configuration
- Verify DEFAULT_FROM_EMAIL is set
- Check email backend is correct
- Enable "Less secure apps" if using Gmail
- Use app-specific password instead of main password

### Issue: Students not appearing as enrolled after approval
**Solution:**
- Check Order items exist
- Verify approve action executed without errors
- Check enrollment records created in database
- Check course total_enrollments incremented

### Issue: Daily classes not visible to students
**Solution:**
- Verify class is_active = True
- Check class date is today or future
- Verify student is enrolled in course (or class is general)
- Check class is created by admin user

### Issue: Screenshot not showing in admin
**Solution:**
- Verify file uploaded and stored
- Check MEDIA_URL and MEDIA_ROOT settings
- Verify file permissions
- Check browser console for image load errors

---

## Summary

This complete implementation provides:
✅ Secure payment verification workflow
✅ Admin interface for payment approval/rejection
✅ Automatic enrollment upon approval
✅ Email notifications for users
✅ Live daily classes feature
✅ Complete documentation and testing guide

The system is production-ready with proper error handling, email notifications, and user-friendly interface.
