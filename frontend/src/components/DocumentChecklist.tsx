"use client";

interface DocItem {
  key: string;
  label: string;
  mandatory?: boolean;
}

const PURCHASE_DOCS: DocItem[] = [
  { key: "sale_deed",         label: "Sale Deed" },
  { key: "chain_docs",        label: "Chain Documents (30 years)" },
  { key: "encumbrance_cert",  label: "Encumbrance Certificate" },
  { key: "mutation_cert",     label: "Mutation Certificate" },
  { key: "approved_plan",     label: "Approved Building Plan" },
  { key: "cc_oc",             label: "CC / OC Certificate" },
  { key: "tax_receipts",      label: "Property Tax Receipts" },
  { key: "pan_aadhaar",       label: "PAN / Aadhaar" },
  { key: "society_docs",      label: "Society Documents" },
  { key: "lpi_cert",          label: "LPI Certificate", mandatory: true },
];

const RENTAL_DOCS: DocItem[] = [
  { key: "rent_agreement",     label: "Rent Agreement" },
  { key: "pan_aadhaar",        label: "PAN / Aadhaar" },
  { key: "police_verification",label: "Police Verification" },
];

interface Props {
  uploadedDocs: string[];
  verifiedDocs: string[];
  transactionType: "buy" | "rent";
}

export default function DocumentChecklist({ uploadedDocs, verifiedDocs, transactionType }: Props) {
  const docs = transactionType === "buy" ? PURCHASE_DOCS : RENTAL_DOCS;

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-100">
        <h3 className="text-sm font-semibold text-gray-700">
          Document Checklist — {transactionType === "buy" ? "Purchase" : "Rental"}
        </h3>
      </div>
      <ul className="divide-y divide-gray-50">
        {docs.map((doc) => {
          const uploaded = uploadedDocs.includes(doc.key);
          const verified = verifiedDocs.includes(doc.key);

          return (
            <li key={doc.key} className="flex items-center gap-3 px-4 py-2.5">
              <span
                className={`w-5 h-5 rounded-full flex-shrink-0 flex items-center justify-center text-xs font-bold ${
                  verified
                    ? "bg-green-500 text-white"
                    : uploaded
                    ? "bg-yellow-400 text-white"
                    : "bg-gray-200 text-gray-400"
                }`}
              >
                {verified ? "✓" : uploaded ? "↑" : "○"}
              </span>
              <span className="text-sm text-gray-700 flex-1">{doc.label}</span>
              {doc.mandatory && (
                <span className="text-xs text-red-500 font-semibold">MANDATORY</span>
              )}
              <span
                className={`text-xs px-2 py-0.5 rounded-full ${
                  verified
                    ? "bg-green-50 text-green-700"
                    : uploaded
                    ? "bg-yellow-50 text-yellow-700"
                    : "bg-gray-100 text-gray-400"
                }`}
              >
                {verified ? "Verified" : uploaded ? "Uploaded" : "Pending"}
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
