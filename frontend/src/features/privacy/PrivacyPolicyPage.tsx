export default function PrivacyPolicyPage() {
  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-6 text-2xl font-bold text-text">Privacy Policy</h1>

      <div className="space-y-6 text-text-muted">
        <section>
          <h2 className="mb-2 text-lg font-semibold text-text">What We Collect</h2>
          <p>
            Weather Kitchen collects only the information needed to provide our recipe discovery
            service: your family name, family size, user names, selected ingredients, and favorite
            recipes. We do not collect email addresses, location data, or any identifying
            information about children.
          </p>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-semibold text-text">How We Use Your Data</h2>
          <p>
            Your data is used exclusively to personalize your recipe recommendations and remember
            your preferences. We do not sell, share, or transfer your data to third parties. There
            is no advertising or tracking in Weather Kitchen.
          </p>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-semibold text-text">Data Storage</h2>
          <p>
            Your data is stored securely on our servers. Authentication uses JWT tokens with
            automatic expiration. Admin PINs are hashed with bcrypt and never stored in plaintext.
          </p>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-semibold text-text">Data Retention</h2>
          <ul className="ml-4 list-disc space-y-1">
            <li>Family and user data: retained while your account is active</li>
            <li>Deleted data: permanently removed after 30 days</li>
            <li>Audit logs: retained for 90 days, then deleted</li>
          </ul>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-semibold text-text">Your Rights (GDPR)</h2>
          <ul className="ml-4 list-disc space-y-1">
            <li>
              <strong>Access &amp; Export:</strong> Download all your data from the Data Management
              page
            </li>
            <li>
              <strong>Deletion:</strong> Request complete deletion of your family data
            </li>
            <li>
              <strong>Portability:</strong> Export your data in JSON format
            </li>
          </ul>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-semibold text-text">Contact</h2>
          <p>
            For privacy questions or data requests, please use the Data Management page in your
            account settings.
          </p>
        </section>
      </div>
    </div>
  );
}
