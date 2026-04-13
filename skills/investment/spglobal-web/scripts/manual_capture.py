# Manual API Capture Instructions

Since automated browser sessions are showing errors, follow these steps to capture the exact API request:

## Step 1: Open Capital IQ in Chrome

1. Open https://www.capitaliq.spglobal.com/ in Chrome
2. Login if needed
3. Navigate to a company page (e.g., Apple: https://www.capitaliq.spglobal.com/web/client?auth=inherit#/company/4004205)

## Step 2: Open DevTools Network Tab

1. Press F12 to open DevTools
2. Click on "Network" tab
3. Filter by "Fetch/XHR" or search for "api" or "profile"

## Step 3: Find the Company Data API Call

Look for requests to URLs containing:
- `/apisv3/`
- `company`
- `profile`
- `4004205` (Apple's ID)

## Step 4: Copy the Request

1. Click on the request
2. Right-click on the request in the Network tab
3. Select "Copy" -> "Copy as cURL (bash)"

## Step 5: Save the cURL Command

Paste the cURL command into a file or share it with me.

---

## Alternative: Browser Console Method

After logging in and navigating to a company page, open the Console tab (F12 -> Console) and run:

```javascript
// Find all API calls
fetch('/apisv3/spg-webplatform-core/company/profile?id=4004205', {
    headers: {
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
})
.then(r => r.json())
.then(data => {
    console.log('Company Data:', data);
    copy(data);  // Copies to clipboard
})
.catch(e => console.error('Error:', e));
```

Or try to find the auth token:

```javascript
// Get cookies as JSON
copy(JSON.stringify(document.cookie.split('; ').map(c => {
    const [name, ...rest] = c.split('=');
    return {name, value: rest.join('=')};
})));
```

## Step 6: Share the Output

Either:
1. Share the cURL command
2. Share the JSON response from the console
3. Share the cookies JSON

This will help identify the correct headers and tokens needed for API access.
