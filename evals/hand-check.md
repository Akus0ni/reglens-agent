# Judge hand check

Run 1 (20261124T140912Z-r1.json, 20261124T152938Z-r1.json). Label each memo with the rubric below, before looking at the judge's scores. Labelled by Claude in the working session without calling the API (D14).

## Rubric

Score the compliance memo on two criteria, each 1 to 5.
grounded: is every finding's stated obligation supported by the text of the passages it cites?
  5 = every finding is fully supported; 3 = mostly supported, with some claims the passages don't make;
  1 = findings claim obligations the passages do not contain.
actionable: are the recommendations specific, correct for the feature described, and something a product team
  could act on? 5 = specific and fitting; 3 = generic or partly off-target; 1 = vague, wrong or missing.
A memo with no findings: grounded 5 if the passages really state no obligation the feature touches, lower if they do;
actionable 5 if saying nothing is right for this feature.

## cf-contacts

```text
<feature>Our digital lending app asks for permission to read the borrower's phone contacts at sign-up. If a loan becomes overdue, our recovery team calls and messages people in the contact list to remind them that the borrower owes us money.</feature>
<findings>
<finding severity="HIGH" cites="1728">Obligation: An NBFC must ensure its digital lending app (and its LSP's app) does not access mobile phone resources such as the contact list, files and media, call logs or telephony functions. Only one-time access to camera, microphone or location is allowed, for onboarding/KYC, with explicit consent.
Recommendation: Remove the contact-list permission from the app at sign-up. Delete any contact data already collected. Audit the app and any LSP apps so none request contacts, files, call logs or telephony access.</finding>
<finding severity="HIGH" cites="2158,2072">Obligation: The NBFC must ensure that it and its agents do not intimidate or harass anyone in debt collection. This includes acts that intrude on the privacy of the debtor's family members, referees and friends, and sending inappropriate messages on mobile or social media. Undue harassment in recovery is also prohibited under the Fair Practices Code.
Recommendation: Stop the recovery team from calling or messaging people in the borrower's contact list. Limit recovery contact to the borrower, and to guarantors or co-obligors where applicable. Observe the calling-hour limits (8:00 a.m. to 7:00 p.m.) and bar any message that tells third parties about the borrower's debt.</finding>
<finding severity="HIGH" cites="1632,2157,1728">Obligation: The NBFC must keep customer information confidential and may not divulge it for any other purpose without the customer's express permission. Recovery agents must observe strict customer confidentiality. Explicit consent is also needed before sharing a borrower's personal information with a third party, unless a statutory or regulatory requirement applies.
Recommendation: Do not tell contacts that the borrower owes money or is in default. Disclose a borrower's debt status only with the borrower's explicit consent, or where the law requires it. Add confidentiality terms to recovery-agent scripts and contracts, and monitor compliance.</finding>
<finding severity="HIGH" cites="1962,1728">Obligation: The notice to a Data Principal must give an itemised description of the personal data and the specified purpose. It must also explain how to withdraw consent and exercise rights. Collecting contact data, which holds third parties' personal data, without a notice that meets these requirements would fail them. Separately, data collection by a digital lending app must be need-based, with prior and explicit consent that has an audit trail.
Recommendation: Stop collecting contacts. If any contact data is retained, check whether a compliant notice and consent exist for it. The third parties whose numbers sit in the borrower's contacts have received no notice, so remove those records.</finding>
<finding severity="MEDIUM" cites="1728">Obligation: Consent must be need-based, and the purpose for which consent is sought must be disclosed at each stage of the borrower interface. The borrower must be able to give or deny consent for specific data uses and to restrict disclosure to third parties. Contact-list data collected at sign-up and then used for recovery goes beyond a need-based, disclosed purpose.
Recommendation: Collect only the data needed for the stated lending purpose. Make sure each consent screen states its purpose and lets the borrower deny or revoke consent for specific data. Do not repurpose sign-up data for recovery contact.</finding>
<finding severity="MEDIUM" cites="2156,2157,1723">Obligation: The NBFC must ensure that recovery agents are trained in privacy of customer information and hours of calling, and that they follow the code of conduct. It must also tell the borrower who the authorised recovery agent is when a loan defaults and an agent is assigned.
Recommendation: Train recovery staff on privacy and permitted contact. Get a signed undertaking to the code of conduct from recovery agents. Tell the borrower the particulars of the assigned recovery agent. Set up a grievance process for recovery complaints.</finding>
</findings>
<passages>
<passage id="1632" document="Reserve Bank of India (Non-Banking Financial Companies – Know Your Customer) Directions, 2025" ref="Para 61">61. Secrecy Obligations and Sharing of Information:
(1) The NBFC shall maintain secrecy regarding the customer information that
arises out of the contractual relationship between the NBFC and the customer.
(2) The NBFC shall treat information collected from customers for the purpose of
opening of account as confidential and shall not divulge details thereof for the purpose
of cross-selling, or for any other purpose without the express permission of the
customer.
(3) While considering the requests for data / information from Government and
other agencies, the NBFC shall satisfy itself that the information being sought is not
of such a nature as will violate the provisions of the laws relating to secrecy in the
transactions.
(4) The exceptions to the said rule shall be as under:
(i) Where disclosure is under compulsion of law,
(ii) Where there is a duty to the public to disclose,
(iii) Where the interest of the NBFC requires disclosure, and
(iv) Where the disclosure is made with the express or implied consent of the
customer.</passage>
<passage id="1723" document="Reserve Bank of India (Non-Banking Financial Companies – Credit Facilities) Directions, 2025" ref="Para 9, part 2 of 2">9. Disclosures to borrowers
(6) In case of a loan default, when a recovery agent is assigned for recovery or
there is a change in the recovery agent already assigned, the particulars of
such recovery agent authorised to approach the borrower for recovery shall be
communicated to the borrower through</passage>
<passage id="1728" document="Reserve Bank of India (Non-Banking Financial Companies – Credit Facilities) Directions, 2025" ref="Para 13">13. Collection, usage and sharing of data with third parties
(1) An NBFC shall ensure that any collection of data by their DLA and DLA of their
LSP is need-based and with prior and explicit consent of the borrower having
audit trail. In any case, an NBFC shall also ensure that DLA of NBFC / LSP
desist from accessing mobile phone resources like file and media, contact list,
call logs, telephony functions, etc. A one-time access can be taken for camera,
microphone, location or any other facility necessary for the purpose of on-
boarding / KYC requirements only, with the explicit consent of the borrower.
(2) The borrower shall be provided with an option to give or deny consent for use
of specific data, restrict disclosure to third parties, data retention, revoke
consent already granted to collect personal data and if required, make the
NBFC / LSP delete / forget the data.
(3) The purpose of obtaining borrowers’ consent needs to be disclosed at each
stage of interface with the borrowers.
(4) Explicit consent of the borrower shall be taken before sharing personal
information with any third party, except for cases where such sharing is
required as per statutory or regulatory requirement.</passage>
<passage id="1962" document="Digital Personal Data Protection Rules, 2025" ref="Rule 3">3. Notice given by Data Fiduciary to Data Principal. —The notice given by the Data Fiduciary to the
Data Principal shall—
(a) be presented and be understandable independently of any other information that has been, is or may
be made available by such Data Fiduciary;
(b) give, in clear and plain language, a fair account of the details necessary to enable the Data Principal
to give specific and informed consent for the processing of her personal data, which shall include,
at the minimum, —
(i) an itemised description of such personal data; and
(ii) the specified purpose or purposes of, and specific description of the goods or services to be
provided or uses to be enabled by, such processing; and
(c) give, the particular communication link for accessing the website or app, or both, of such Data
Fiduciary, and a description of other means, if any, using which such Data Principal may—
(i) withdraw her consent, with the ease of doing so being comparable to that with which
such consent was given;
(ii) exercise her rights under the Act; and
(iii) make a complaint to the Board.</passage>
<passage id="2072" document="Reserve Bank of India (Non-Banking Financial Companies – Responsible Business Conduct) Directions, 2025" ref="Para 20">20. In the matter of recovery of loans, an NBFC shall not resort to undue harassment
viz., persistently bothering the borrowers at odd hours, use muscle power for
recovery of loans, etc. As complaints from customers also include rude behaviour
from the staff of the companies, an NBFC shall ensure that the staff is adequately
trained to deal with the customers in an appropriate manner.</passage>
<passage id="2156" document="Reserve Bank of India (Non-Banking Financial Companies – Responsible Business Conduct) Directions, 2025" ref="Para 98">98. The NBFC shall ensure that the DSA / DMA / recovery agents are properly trained
to handle their responsibilities with care and sensitivity, particularly aspects such
as soliciting customers, hours of calling, privacy of customer information and
conveying the correct terms and conditions of the p</passage>
<passage id="2157" document="Reserve Bank of India (Non-Banking Financial Companies – Responsible Business Conduct) Directions, 2025" ref="Para 99">99. The NBFC shall obtain the undertaking of DSA / DMA / recovery agents to abide
by the code of conduct. In addition, recovery agents shall adhere to extant
instructions on Fair Practices Code for NBFCs as also its own code for collection
of dues and repossession of security. It is essential that the recovery agents refrain
from any action that could damage the integrity and reputation of the NBFC and
that they observe strict customer confidentiality.</passage>
<passage id="2158" document="Reserve Bank of India (Non-Banking Financial Companies – Responsible Business Conduct) Directions, 2025" ref="Para 100">100.The NBFC shall strictly ensure that it or its agents do not resort to intimidation or
harassment of any kind, either verbal or physical, against any person in their debt
collection efforts, including acts intended to humiliate publicly or intrude upon the
privacy of the debtors' family members, referees and friends, sending
inappropriate messages either on mobile or through social media, making
threatening and/ or anonymous calls, persistently calling the borrower and/ or
calling the borrower before 8:00 a.m. and after 7:00 p.m. for recovery of overdue
loans, making false and misleading representations, etc. These directions shall
not be applicable to microfinance loans.</passage>
</passages>
```

## cf-data-abroad

```text
<feature>Our digital lending app stores all borrower data, including bank statements and KYC documents, on a cloud region in Singapore to reduce cost.</feature>
<findings>
<finding severity="HIGH" cites="1729">Obligation: An NBFC must ensure all data is stored only on servers located within India. Data processed outside India must be deleted from foreign servers and brought back to India within 24 hours of processing.
Recommendation: Move all borrower data, including bank statements and KYC documents, to servers located in India. Do not use the Singapore cloud region for storage. If any processing happens abroad, delete the data there and return it to India within 24 hours. Weigh cost against this hard localisation requirement.</finding>
<finding severity="MEDIUM" cites="1728,1729">Obligation: Data collection by the DLA must be need-based, with prior explicit consent and an audit trail. Borrowers must be able to deny or revoke consent, restrict disclosure and retention, and ask for deletion. The purpose must be disclosed at each stage. LSPs may store only minimal basic personal data, and the NBFC stays responsible for privacy and security.
Recommendation: Check that each data item stored, including bank statements, is need-based and covered by explicit, purpose-specific consent with an audit trail. Provide consent withdrawal and deletion controls. Confirm that any LSP holds only minimal data. Publish a storage policy covering data types, retention, destruction and breach handling.</finding>
<finding severity="MEDIUM" cites="1616,1729">Obligation: The NBFC must preserve customer identification records and transaction records for at least five years after the relationship ends. It must be able to retrieve them quickly and give them to competent authorities promptly on request. The passage sets no location rule of its own, but the digital lending directions require data to be held on servers in India.
Recommendation: Make sure KYC records held in Singapore can be retrieved quickly and produced on request. Moving them to India-located servers resolves both the retrieval concern and the localisation issue. Set retention to at least five years after the relationship ends.</finding>
<finding severity="LOW" cites="1978">Obligation: Personal data may be transferred outside India, but the Data Fiduciary must meet any requirements the Central Government specifies for making the data available to a foreign State or its entities or agencies.
Recommendation: Track any government orders under Rule 15 that apply to the Singapore storage. Note that the RBI localisation requirement is stricter than the DPDP transfer rule and still applies.</finding>
<finding severity="MEDIUM" cites="1965,1966">Obligation: The Data Fiduciary must take reasonable security safeguards, including for processing by a Data Processor. These include encryption or masking, access controls, logging and monitoring, backups, one-year log retention, and contract terms with the processor on security. On a breach it must notify each affected Data Principal without delay and notify the Board, with a detailed report within 72 hours.
Recommendation: Confirm that the cloud contract includes security safeguards, access control, logging and backups. Encrypt the stored data. Set up a breach-response process that can notify borrowers and the Board within the required timelines, including when the breach occurs at the cloud provider.</finding>
<finding severity="MEDIUM" cites="1719,1729,1730">Obligation: The NBFC remains fully responsible and liable for the acts and omissions of its LSPs. It must carry out due diligence on the LSP's data privacy and storage systems and review its conduct periodically. It must publicly disclose its data storage policy and privacy policy on its website and DLA.
Recommendation: Treat the cloud provider and any LSP as under the NBFC's accountability. Assess their storage systems and review their conduct periodically. Make sure the published privacy and storage policies accurately describe where and how data is stored.</finding>
</findings>
<passages>
<passage id="1616" document="Reserve Bank of India (Non-Banking Financial Companies – Know Your Customer) Directions, 2025" ref="Para 47">47. The NBFC shall take the following steps regarding maintenance,
preservation and reporting of customer information, with reference to provisions of
PML Act and Rules. The NBFC shall,
(1) maintain all necessary records of transactions between the NBFC and the
customer, both domestic and international, for at least five years from the date of
transaction;
(2) preserve the records pertaining to the identification of the customers and their
addresses, obtained while opening the account and during the course of business
relationship, for at least five years after the business relationship has ended;
(3) swiftly make available, the identification records and transaction data to the
competent authorities upon request;
(4) introduce a system of maintaining proper records of transactions prescribed
under Rule 3 of Prevention of Money Laundering (Maintenance of Records) Rules,
2005 (PML Rules, 2005);
(5) maintain all necessary information in respect of transactions prescribed under
PML Rule 3 to permit the reconstruction of an individual transaction, including the
following:
(i) the nature of the transactions;
(ii) the amount of the transaction and the currency in which it was denominated;
(iii) the date on which the transaction was conducted; and
(iv) the parties to the transaction.
(6) evolve a system for proper maintenance and preservation of account
information in a manner that allows the NBFC to retrieve data easily and quickly
whenever required or when competent authorities request it;
(7) maintain records of the identity and address of its customers, and records in
respect of transactions referred to in Rule 3 in hard or soft format.
Explanation: For the purpose of this paragraph, the expressions ‘records
pertaining to the identification’, ‘identification records’, etc., shall include
updated records of the identification data, account files, business correspondence,
and results of any analysis undertaken.</passage>
<passage id="1719" document="Reserve Bank of India (Non-Banking Financial Companies – Credit Facilities) Directions, 2025" ref="Para 6">6. Due diligence requirements with respect to LSPs
(1) Digital lending by an NBFC involving a LSP, shall be carried out under a
contractual agreement between the NBFC and the LSP, which clearly defines
the respective roles, rights, and obligations of each party thereto.
(2) An NBFC shall conduct enhanced due diligence before they enter into an
agreement with a LSP for digital lending, taking into account LSP’s technical
capabilities, robustness of data privacy policies and storage systems, fairness
in conduct with borrowers, past records of conduct and ability to comply with
all applicable regulations and statutes.
(3) An NBFC shall carry out periodic review of the conduct of the LSP vis-à-vis the
terms of the contractual agreement and shall take appropriate action in the
event of any deviation therefrom.
(4) An NBFC shall lay down, as part of its policy, suitable monitoring mechanisms
for the loan portfolios originated with the support of LSPs.
(5) An NBFC shall impart necessary guidance to LSP acting as a recovery agent,
to discharge their duties responsibly and ensure that LSP complies with the
applicable instructions under Reserve Bank of India (Non-Banking Financial
Companies – Responsible Business Conduct) Directions, 2025, and other
relevant instructions as issued from time to time.
(6) An NBFC shall continue to conform to the extant guidelines on outsourcing (as
specified under Reserve Bank of India (Non-Banking Financial Companies –
Managing Risks in Outsourcing) Directions, 2025) and shall ensure that the
LSPs engaged by them and the DLAs (either of the NBFC or of the LSPs
engaged by the NBFC) comply with these Directions.
(7) As an overarching principle, any outsourcing agreement entered into by an
NBFC with an LSP shall in no manner dilute or absolve the NBFC of its
obligations under any statutory or regulatory provision, and the NBFC shall
remain fully responsible and liable for all acts and omissions of the LSP.</passage>
<passage id="1728" document="Reserve Bank of India (Non-Banking Financial Companies – Credit Facilities) Directions, 2025" ref="Para 13">13. Collection, usage and sharing of data with third parties
(1) An NBFC shall ensure that any collection of data by their DLA and DLA of their
LSP is need-based and with prior and explicit consent of the borrower having
audit trail. In any case, an NBFC shall also ensure that DLA of NBFC / LSP
desist from accessing mobile phone resources like file and media, contact list,
call logs, telephony functions, etc. A one-time access can be taken for camera,
microphone, location or any other facility necessary for the purpose of on-
boarding / KYC requirements only, with the explicit consent of the borrower.
(2) The borrower shall be provided with an option to give or deny consent for use
of specific data, restrict disclosure to third parties, data retention, revoke
consent already granted to collect personal data and if required, make the
NBFC / LSP delete / forget the data.
(3) The purpose of obtaining borrowers’ consent needs to be disclosed at each
stage of interface with the borrowers.
(4) Explicit consent of the borrower shall be taken before sharing personal
information with any third party, except for cases where such sharing is
required as per statutory or regulatory requirement.</passage>
<passage id="1729" document="Reserve Bank of India (Non-Banking Financial Companies – Credit Facilities) Directions, 2025" ref="Para 14">14. Storage of data
(1) An NBFC shall ensure that LSP engaged by them do not store personal
information of borrower except some basic minimal data (viz., name, address,
contact details of the customer, etc.) that may be required to carry out their
operations or service within the scope of the NBFC-LSP agreement.
Responsibility regarding data privacy and security of the customer’s personal
information on an ongoing basis shall be that of the NBFC.
(2) An NBFC shall ensure that clear policy guidelines regarding the storage of
customer data including the type of data that can be stored, the length of time
for which data can be stored, restrictions on the use of data, data destruction
protocol, standards for handling security breach, etc., are put in place and also
disclosed by the NBFC and the LSP engaged by the NBFC prominently on
their website and DLA at all times.
(3) An NBFC shall ensure that no biometric data is stored / collected by the NBFC
and LSP, unless allowed under extant statutory guidelines.
(4) An NBFC shall ensure that all data is stored only in servers located within India,
while ensuring compliance with statutory obligations/ regulatory instructions.
Further, in case the data is processed outside India, the same shall be deleted
from servers outside India and brought back to India within 24 hours of
processing.</passage>
<passage id="1730" document="Reserve Bank of India (Non-Banking Financial Companies – Credit Facilities) Directions, 2025" ref="Para 15">15. Comprehensive privacy policy
(1) An NBFC and their LSPs shall have a comprehensive privacy policy compliant
with applicable laws, associated regulations and RBI guidelines which shall be
made available publicly on the website of the NBFC and LSP, as the case may
be.
(2) Details of third parties (where applicable) allowed to collect personal
information through the DLA shall also be disclosed in the privacy policy.</passage>
<passage id="1965" document="Digital Personal Data Protection Rules, 2025" ref="Rule 6">6. Reasonable security safeguards. — (1) A Data Fiduciary shall protect personal data in its possession or
under its control, including in respect of any processing undertaken by it or on its behalf by a Data
Processor, by taking reasonable security safeguards to prevent personal data breach, which shall include, at
the minimum, —
(a) appropriate data security measures, such as securing of personal data through encryption,
obfuscation, masking or the use of virtual tokens mapped to that personal data;
(b) appropriate measures to control access to the computer resources used by such Data Fiduciary or
such a Data Processor, wherever applicable;
(c) visibility on the accessing of such personal data, through appropriate logs, monitoring and review,
for enabling detection of unauthorised access, its investigation and remediation to prevent
recurrence;
(d) reasonable measures for continued processing in the event of confidentiality, integrity or
availability of such personal data being compromised as a result of destruction or loss of access to
personal data or otherwise, such as by way of data-backups;
(e) for enabling the detection of unauthorised access, its investigation, remediation to prevent
recurrence and continued processing in the event of such a compromise, retain such logs and
personal data for a period of one year, unless compliance with any law for the time being in force
requires otherwise;
(f) appropriate provision in the contract entered into between such Data Fiduciary and such a Data
Processor, wherever applicable, for taking reasonable security safeguards; and
(g) appropriate technical and organisational measures to ensure effective observance of security
safeguards.
(2) In this rule, the expression “computer resource” shall have the same meaning as is assigned to it in
Information Technology Act, 2000 (21 of 2000).</passage>
<passage id="1966" document="Digital Personal Data Protection Rules, 2025" ref="Rule 7">7. Intimation of personal data breach. — (1) On becoming aware of any personal data breach, the Data
Fiduciary shall, to the best of its knowledge, intimate to each affected Data Principal, in a concise, clear and
plain manner and without delay, through her user account or any mode of communication registered by her
with the Data Fiduciary, —
(a) a description of the breach, including its nature, extent and the timing of its occurrence;
(b) the consequences relevant to her, that are likely to arise from the breach;
(c) the measures implemented and being implemented by the Data Fiduciary, if any, to mitigate risk;
(d) the safety measures that she may take to protect her interests; and
(e) business contact information of a person who is able to respond on behalf of the Data Fiduciary, to
queries, if any, of the Data Principal.
(2) On becoming aware of any personal data breach, the Data Fiduciary shall intimate to the Board, —
(a) without delay, a description of the breach, including its nature, extent, timing and location of
occurrence and the likely impact;
(b) within seventy-two hours of becoming aware of the breach, or within such longer period as the
Board may allow on a request made in writing in this behalf, —
(i) updated and detailed information in respect of such description;
(ii) the broad facts related to the events, circumstances and reasons leading to the breach;
(iii) measures implemented or proposed, if any, to mitigate risk;
(iv) any findings regarding the person who caused the breach;
(v) remedial measures taken to prevent recurrence of such breach; and
(vi) a report regarding the intimations given to affected Data Principals.</passage>
<passage id="1978" document="Digital Personal Data Protection Rules, 2025" ref="Rule 15">15. Transfer of personal data outside the territory of India.— Any personal data processed by a Data
Fiduciary under the Act may be transferred outside the territory of India subject to the restriction that the
Data Fiduciary shall meet such requirements as the Central Government may, by general or special order,
specify in respect of making such personal data available to any foreign State, or to any person or entity
under the control of or any agency of such a State.</passage>
</passages>
```

## cf-disbursal-via-lsp

```text
<feature>For loans sourced through our lending service provider's app, we disburse the loan amount into the LSP's pool account, and the LSP transfers it to the borrower after deducting its own service fee.</feature>
<findings>
<finding severity="HIGH" cites="1724">Obligation: An NBFC must always disburse a loan into the borrower's bank account. Narrow exceptions apply: statutory or regulatory mandates, co-lending flows between lenders, and specific end-use disbursals paid directly to the end-beneficiary. Disbursal to a third-party account, including an LSP's account, is not permitted.
Recommendation: Stop disbursing into the LSP's pool account. Disburse directly into each borrower's bank account and make sure the LSP has no direct or indirect control over the flow of funds.</finding>
<finding severity="HIGH" cites="1725">Obligation: Fees, charges and reimbursements payable to the LSP must be paid directly by the NBFC. The LSP must not charge or collect them from borrowers separately.
Recommendation: Remove the LSP's deduction of its service fee from the loan amount. Pay the LSP's fee from the NBFC's own funds under the contract and disburse the full net amount to the borrower.</finding>
<finding severity="MEDIUM" cites="2082,2056,1722">Obligation: The KFS must show the sanctioned amount, fees payable to the NBFC and to third parties routed through the NBFC, and the net disbursed amount. The APR is computed on the net disbursed amount using the IRR approach and reducing balance method. APR includes the interest rate and all other charges associated with the credit facility.
Recommendation: Make sure the KFS and APR calculation reflect the actual charges and net disbursed amount. Once the LSP fee is paid by the NBFC and not deducted from the borrower, check that the KFS does not misstate net disbursal or APR.</finding>
<finding severity="MEDIUM" cites="1719">Obligation: The NBFC must have a contractual agreement defining roles with the LSP and conduct enhanced due diligence before engaging it. It must review the LSP's conduct periodically and monitor LSP-originated portfolios. It must follow the outsourcing directions and ensure the LSP complies with these Directions. The NBFC remains fully responsible for the LSP's acts and omissions.
Recommendation: Review the LSP agreement and due diligence file. Add controls and monitoring so the LSP cannot hold or deduct borrower funds, and take action on the deviation already seen in the pool-account and fee-deduction flow.</finding>
<finding severity="HIGH" cites="1724">Obligation: Loan servicing and repayment must go directly into the NBFC's bank account, without any pass-through or pool account of a third party, including the LSP. Flows of funds between the borrower and NBFC bank accounts must not be controlled directly or indirectly by the LSP. The pool-account model cannot be reconciled with these rules.
Recommendation: Redesign disbursement and repayment flows so funds move only between the NBFC's and the borrower's bank accounts. Do not try to reconcile the pool-account arrangement. Remove it and confirm that repayments also bypass LSP accounts.</finding>
</findings>
<passages>
<passage id="1719" document="Reserve Bank of India (Non-Banking Financial Companies – Credit Facilities) Directions, 2025" ref="Para 6">6. Due diligence requirements with respect to LSPs
(1) Digital lending by an NBFC involving a LSP, shall be carried out under a
contractual agreement between the NBFC and the LSP, which clearly defines
the respective roles, rights, and obligations of each party thereto.
(2) An NBFC shall conduct enhanced due diligence before they enter into an
agreement with a LSP for digital lending, taking into account LSP’s technical
capabilities, robustness of data privacy policies and storage systems, fairness
in conduct with borrowers, past records of conduct and ability to comply with
all applicable regulations and statutes.
(3) An NBFC shall carry out periodic review of the conduct of the LSP vis-à-vis the
terms of the contractual agreement and shall take appropriate action in the
event of any deviation therefrom.
(4) An NBFC shall lay down, as part of its policy, suitable monitoring mechanisms
for the loan portfolios originated with the support of LSPs.
(5) An NBFC shall impart necessary guidance to LSP acting as a recovery agent,
to discharge their duties responsibly and ensure that LSP complies with the
applicable instructions under Reserve Bank of India (Non-Banking Financial
Companies – Responsible Business Conduct) Directions, 2025, and other
relevant instructions as issued from time to time.
(6) An NBFC shall continue to conform to the extant guidelines on outsourcing (as
specified under Reserve Bank of India (Non-Banking Financial Companies –
Managing Risks in Outsourcing) Directions, 2025) and shall ensure that the
LSPs engaged by them and the DLAs (either of the NBFC or of the LSPs
engaged by the NBFC) comply with these Directions.
(7) As an overarching principle, any outsourcing agreement entered into by an
NBFC with an LSP shall in no manner dilute or absolve the NBFC of its
obligations under any statutory or regulatory provision, and the NBFC shall
remain fully responsible and liable for all acts and omissions of the LSP.</passage>
<passage id="1722" document="Reserve Bank of India (Non-Banking Financial Companies – Credit Facilities) Directions, 2025" ref="Para 9, part 1 of 2">9. Disclosures to borrowers
(1) An NBFC shall provide a Key Fact Statement (KFS), as per instructions
contained in Reserve Bank of India (Non- Banking Financial Companies –
Responsible Business Conduct) Directions, 2025.
(2) As regards penal charges, an NBFC shall be guided by Reserve Bank of India
</passage>
<passage id="1724" document="Reserve Bank of India (Non-Banking Financial Companies – Credit Facilities) Directions, 2025" ref="Para 10, part 1 of 2">10. Loan disbursal, servicing and repayment
(1) Disbursement of loan by an NBFC shall always be made into the bank account
of the borrower except for disbursals covered exclusively under statutory or
regulatory mandate (of the Reserve Bank or of any other regulator), flow of
money between lenders for co-lending transactions and disbursals for specific
end use, provided the loan is disbursed directly into the bank account of the
end-beneficiary. An NBFC shall ensure that in no case, disbursal is made to a
third-party account, including the accounts of LSP, except as provided for in
this Chapter on ‘Digital Lending’.
Provided that advances against salary, where the loan is disbursed directly to
the bank account of the borrower, but the repayment is from the corporate
employer, can be allowed subject to the condition that the loan is repaid by the
corporate employer by deducting the amount from the borrower’s salary.
However, it must be ensured that LSPs do not have any control over the flow
of funds directly or indirectly in such transactions and that repayment is directly
from the bank account of the employer to the NBFC.
Note: Co-lending arrangements shall be governed by the Reserve Bank of
India (Non- Banking Financial Companies – Transfer and Distribution of Credit
Risk) Directions, 2025, subject to the condition that no third party other than
the lenders in a co-lending transaction shall have direct or indirect control over
the flow of funds at any point of time.
(2) An NBFC shall ensure that all loan servicing, repayment, etc. is executed by
the borrower directly in the NBFC’s bank account without any pass-through
account/ pool account of any third party, including the accounts of LSP.
(3) The flow of funds between the bank accounts of the borrower and the NBFC
shall not be controlled either directly or indirectly by a third-party, including the
LSP.</passage>
<passage id="1725" document="Reserve Bank of India (Non-Banking Financial Companies – Credit Facilities) Directions, 2025" ref="Para 10, part 2 of 2">10. Loan disbursal, servicing and repayment
(4) An NBFC shall ensure that any fees, charges, reimbursements, etc. payable
to LSP are paid directly by the NBFC and are not charged to or collected from
the borrowers separately by LSP.
(5) In case of delinquent loans, an NBFC may deploy physical interface to recover
loans in cash, wherever necessary. In order to afford operational flexibility to
the NBFC, such transactions are exempted from the requirement of direct
repayment of loan in the NBFC’s bank account. However, any recovery by cash
shall be duly reflected in full in the borrower’s account on the same day and
the NBFC shall ensure that any fees, charges, etc., payable to LSPs for such
recovery are paid directly by the NBFC and are not charged by LSP to the
borrower either directly or indirectly from the recovery proceeds.</passage>
<passage id="2056" document="Reserve Bank of India (Non-Banking Financial Companies – Responsible Business Conduct) Directions, 2025" ref="Para 6, part 1 of 2">6. In these Directions, unless the context states otherwise, the terms herein shall bear
the meaning assigned to them below:
(1) Annual Percentage Rate (APR) means the annual cost of credit to the
borrower which includes interest rate and all other charges associated with the
credit facility.
(2) Co</passage>
<passage id="2082" document="Reserve Bank of India (Non-Banking Financial Companies – Responsible Business Conduct) Directions, 2025" ref="Para 29, part 2 of 3">29. The following instructions shall be applicable in case of all new retail and MSME
(i) Illustration for computation of APR for Retail and MSME loans
Sl.
No.
Parameter Details
1 Sanctioned Loan amount (in Rupees) (Sl. No. 2 of the
KFS template – Part 1)
20,000
2 Loan Term (in years/ months/ days) (Sl. No.4 of the KFS
template – Part 1)
a) No. of instalments for payment of principal, in case of
non-equated periodic loans
-
b) Type of EPI
Amount of each EPI (in Rupees) and
nos. of EPIs (e.g., no. of EMIs in case of monthly
instalments)
(Sl. No. 5 of the KFS template – Part 1)
Monthly
c) No. of instalments for payment of capitalised interest, if
any
-
d) Commencement of repayments, post sanction (Sl. No. 5
of the KFS template – Part 1)
30 days
3 Interest rate type (fixed or floating or hybrid) (Sl. No. 6 of
the KFS template – Part 1)
Fixed
4 Rate of Interest (Sl. No. 6 of the KFS template – Part 1) 15 %
5 Total Interest Amount to be charged during the entire
tenor of the loan as per the rate prevailing on sanction
date (in Rupees)
3,274
6 Fee/ Charges payable (in Rupees)
Note: Where such charges cannot be determined prior to
sanction, NBFCs may indicate an upper ceiling
A Payable to the NBFC (Sl. No.8A of the KFS template-Part
1)
B Payable to third-party routed through NBFC (Sl. No.8B of
the KFS template – Part 1)
7 Net disbursed amount (1-6) (in Rupees) 19,600
8 Total amount to be paid by the borrower (sum of 1 and 5)
(in Rupees)
23,274*
9 Annual Percentage Rate- Effective annualized interest
rate (in percentage) (Sl. No.9 of the KFS template-Part
1)
Note: Computed on net disbursed amount using IRR
approach and reducing balance method
17.07%
10 Schedule of disbursement as per terms and conditions Detailed
schedule to
be provided
11 Due date of payment of instalment and interest DDMMYYYY
* The difference in repayment amount calculated from the total of instalments given under the detailed</passage>
</passages>
```

## cf-no-cooling-off

```text
<feature>Once a digital loan is disbursed it cannot be cancelled. A borrower who wants to exit early pays the full foreclosure charge of 3% of the principal, even on the day after disbursal.</feature>
<findings>
<finding severity="HIGH" cites="1726">Obligation: A digital loan borrower must be given an explicit option to exit during a cooling-off period of at least one day by paying only the principal and proportionate APR, without penalty. The NBFC may retain only a reasonable one-time processing fee, disclosed upfront in the KFS.
Recommendation: Remove the no-cancellation rule and the 3% charge for early exit. Build a cooling-off exit of at least one day where the borrower repays principal plus proportionate APR, with at most a reasonable one-time processing fee disclosed in the KFS. Exits the day after disbursal must fall inside this window unless the credit policy sets a longer one.</finding>
<finding severity="MEDIUM" cites="2091,2090,2139,2092">Obligation: No pre-payment charges may be levied on floating rate loans for non-business purposes to individuals (existing loans under Para 33, and loans sanctioned or renewed from 1 January 2026 under Para 34(1)). Business-purpose floating rate loans to individuals and MSEs are also barred from charges, depending on NBFC layer and loan size. Microfinance loans cannot carry any pre-payment charge. In other cases, charges follow the approved policy and, for term loans, must be based on the amount being prepaid. No charge may be levied where pre-payment is at the NBFC's instance.
Recommendation: The feature does not say whether loans are floating or fixed rate, personal or business, or microfinance. Check each loan product against these prohibitions and switch off the 3% charge where it is barred. Where a charge is allowed, make sure it is covered by the Board-approved policy and is levied on the amount prepaid. Also confirm no charge applies when the NBFC initiates the pre-payment.</finding>
<finding severity="MEDIUM" cites="2092,2169">Obligation: The applicability of pre-payment charges must be clearly disclosed in the sanction letter and loan agreement, and in the KFS where one is required. Foreclosure charges appear under contingent charges in the KFS format. No undisclosed pre-payment charge may be levied.
Recommendation: Show the 3% foreclosure charge, and the cases where it applies, in the sanction letter, loan agreement and KFS (contingent charges, item 10(iii)) before the borrower accepts. Block any levy that was not disclosed in this way.</finding>
<finding severity="LOW" cites="2066,2077">Obligation: Fair practice requires that loan terms and conditions be conveyed in writing, and that a copy of the loan agreement and its enclosures be given to the borrower at sanction or disbursement. Failing to do so is an unfair practice. The Reserve Bank has also flagged excessive interest and charges as a concern.
Recommendation: Make sure the no-cancellation term and the 3% foreclosure charge are plainly stated in the borrower's agreement copy. Review whether a full 3% charge the day after disbursal is reasonable under the fair practices code and the Board's charges policy.</finding>
</findings>
<passages>
<passage id="1726" document="Reserve Bank of India (Non-Banking Financial Companies – Credit Facilities) Directions, 2025" ref="Para 11">11. Cooling-off period
(1) The borrower shall be given an explicit option to exit a digital loan by paying
the principal and the proportionate APR without any penalty during an initial
“cooling-off period”. The cooling off period shall be determined by the NBFC in
terms of their credit policy, subject to the period so determined not being less
than one day. For borrower continuing with the loan even after cooling-off
period, pre-payment shall continue to be allowed as per Reserve Bank of India
(Non-Banking Financial Companies- Responsible Business Conduct)
Directions, 2025.
(2) An NBFC may retain a reasonable one-time processing fee, if the customer
exits the loan during the cooling-off period. This, if applicable, shall be
disclosed to the customer upfront in KFS.</passage>
<passage id="2066" document="Reserve Bank of India (Non-Banking Financial Companies – Responsible Business Conduct) Directions, 2025" ref="Para 14">14. Borrowers may not be fully aware of the terms and conditions of the loans including
rate of interest at the time of sanction of loans, either because the NBFC does not
provide details of the same or the borrower has no time to look into detailed
agreement. Not furnishing a copy of the loan agreement or enclosures quoted in
the loan agreement is an unfair practice and this could lead to disputes between
the NBFC and the borrower with regard to the terms and conditions. The NBFC,
shall furnish a copy of the loan agreement as understood by the borrower along
with a copy each of all enclosures quoted in the loan agreement to all the borrowers
at the time of sanction / disbursement of loans.</passage>
<passage id="2077" document="Reserve Bank of India (Non-Banking Financial Companies – Responsible Business Conduct) Directions, 2025" ref="Para 25">25. The Reserve Bank has been receiving several complaints regarding levying of
excessive interest and charges on certain loans and advances by NBFCs. Though
interest rates are not regulated by the Reserve Bank, rates of interest beyond a
certain level may be seen to be excessive and can neither be </passage>
<passage id="2090" document="Reserve Bank of India (Non-Banking Financial Companies – Responsible Business Conduct) Directions, 2025" ref="Para 33">33. In case of existing loans sanctioned or renewed on or before December 31, 2025,
an NBFC shall not levy pre-payment charges on any floating rate term loan
sanctioned for purposes other than business to individual borrowers, with or
without co-obligant(s).</passage>
<passage id="2091" document="Reserve Bank of India (Non-Banking Financial Companies – Responsible Business Conduct) Directions, 2025" ref="Para 34, part 1 of 2">34. An NBFC shall adhere to the following directions regarding levy of pre-payment
charges on loans and advances (term loans as well as demand loans) sanctioned
or renewed on or after January 1, 2026:
(1) For all floating rate loans granted for purposes other than business to
individuals, with or without co-obligant(s), an NBFC shall not levy pre-payment
charges.
(2) For all floating rate loans granted for business purpose to individuals and Micro
and Small Enterprises (MSEs), as defined in Micro, Small and Medium
Enterprises Development (MSMED) Act, 2006, with or without co-obligant(s):
(i) an NBFC-Upper Layer shall not levy any pre-payment charges.
(ii) an NBFC-Middle Layer shall not levy any pre-payment charges on loans
with sanctioned amount/ limit up to ₹50 lakh.
(3) The Directions at paragraphs 34(1) and 34(2) above shall be applicable
irrespective of the source of funds used for pre-payment of loans, either in part
or in full, and without any minimum lock-in period.
(4) Applicability of above Directions for dual/ special rate (combination of fixed and
floating rate) loans will depend on whether the loan is on floating rate at the
time of pre-payment.
(5) In cases other than those mentioned at paragraphs 34(1) and 34(2) above, pre-
payment charges, if any, shall be as per the approved policy of the NBFC.
However, in case of term loans, pre-payment charges, if levied by the NBFC,
shall be based on the amount being prepaid. In case of cash credit/ overdraft
facilities, pre-payment charges on closure of the facility before the due date
shall be levied on an amount not exceeding the sanctioned limit.
(6) In case of cash credit/ overdraft facilities, no pre-payment charges shall be
applicable if the borrower intimates the NBFC of her / his / its intention not to
renew the facility before the period as stipulated in the loan agreement,
provided that the facility gets closed on the due date.</passage>
<passage id="2092" document="Reserve Bank of India (Non-Banking Financial Companies – Responsible Business Conduct) Directions, 2025" ref="Para 34, part 2 of 2">34. An NBFC shall adhere to the following directions regarding levy of pre-payment
(7) An NBFC shall not levy any charges where pre-payment is effected at the
instance of the NBFC.
(8) The applicability or otherwise of pre-payment charges shall be clearly disclosed
in the sanction letter and loan agreement. Further, in case of loans and
advances where Key Facts Statement (KFS) is to be provided as specified in
paragraph 29, the same shall also be mentioned in the KFS. No pre-payment
charges which have not been disclosed as specified herein shall be charged by
the NBFC.
(9) The NBFC shall not levy any charges / fees retrospectively at the time of pre-
payment of loans, which were waived off earlier by the NBFC.</passage>
<passage id="2139" document="Reserve Bank of India (Non-Banking Financial Companies – Responsible Business Conduct) Directions, 2025" ref="Para 81">81. There shall be no pre-payment charge levied on microfinance loans. Charges, if
any, for delayed payment shall be applied on the overdue amount and not on the
entire loan amount.</passage>
<passage id="2169" document="Reserve Bank of India (Non-Banking Financial Companies – Responsible Business Conduct) Directions, 2025" ref="Annex I, part 1 of 2">Part 1 (Interest rate and fees / charges)
1 Loan proposal/ account
No.
Type of Loan
2 Sanctioned Loan amount (in
Rupees)
3 Disbursal schedule
(i) Disbursement in stages or 100%
upfront.
(ii) If it is stage wise, mention the clause
of loan agreement having relevant
details
4 Loan term (year/months/days)
5 Instalment details
Type of instalments Number of EPIs EPI (₹) Commencement of
repayment, post sanction
6 Interest rate (%) and type (fixed or floating or
hybrid)
7 Additional Information in case of Floating rate of interest
Referen
ce
Benchm
ark
Benchm
ark rate
(%) (B)
Spread (%)
(S)
Final rate
(%)
R = (B) +
(S)
Reset
periodicity*
(Months)
Impact of change in
the reference
benchmark
(for 25 bps change
in ‘R’, change in:)
B S EPI (₹) No. of
EPIs
8 Fee/ Charges (An NBFC may disclose the amount net of any taxes such as GST)
Payable to the NBFC (A) Payable to a third party
through the NBFC (B)
One-time/
Recurring
Amount (in
₹) or
Percentag
e (%) as
applicable
(Mention
frequency,
where
recurring)
One-
time/Rec
urring
Amount (in
₹) or
Percentag
e (%) as
applicable
(Mention
frequency,
where
recurring)
(i) Processing fees
(ii) Insurance charges
(iii) Valuation fees
(iv) Any other (please
specify)
9 Annual Percentage Rate (APR) (%)
(Please refer to the illustration in sub-
paragraph (3) of paragraph 29 of these
directions)
10 Details of Contingent Charges (in ₹ or %, as applicable)
(i) Penal charges, if any, in case of delayed payment
(ii) Other penal charges, if any
(iii) Foreclosure charges, if applicable
(iv) Charges for switching of loans from floating to fixed rate and
vice versa</passage>
</passages>
```

## dpdp-breach-notice

```text
<feature>If our customer database is breached, our incident plan is to email affected customers within 30 days once the investigation is complete. We do not plan to inform any regulator or board.</feature>
<findings>
<finding severity="HIGH" cites="1966">Obligation: On becoming aware of a personal data breach, the Data Fiduciary must intimate the Data Protection Board without delay with a description of the breach, and within 72 hours (or a longer period the Board allows) give detailed information, including the facts, mitigation, findings on the cause, remedial measures and a report on intimations to Data Principals.
Recommendation: Change the incident plan to include notifying the Board without delay and filing the detailed report within 72 hours of becoming aware of the breach. Assign an owner and prepare templates for both filings.</finding>
<finding severity="HIGH" cites="1966">Obligation: The Data Fiduciary must tell each affected Data Principal, without delay, about the breach: its nature, extent and timing, the likely consequences, the mitigation measures, the safety steps the person can take, and a business contact. The notice must be concise, clear and plain, and sent through the user account or a registered communication mode.
Recommendation: Replace the plan to wait 30 days until the investigation ends with notice to customers without delay on becoming aware of the breach. Use a notice template covering items (a) to (e), and send updates as the investigation progresses.</finding>
<finding severity="MEDIUM" cites="1965">Obligation: The Data Fiduciary must maintain reasonable security safeguards, at minimum including encryption or masking, access controls, logs, monitoring and review to detect and investigate unauthorised access, and data backups. It must also retain logs and personal data for one year to support detection, investigation and remediation, and must have appropriate contract terms with Data Processors.
Recommendation: The plan describes no detection, logging or investigation capability. Confirm that logging, monitoring and review, one-year log retention, backups, access control and processor contract clauses are in place, so that a breach can be detected and investigated quickly.</finding>
<finding severity="MEDIUM" cites="1729,1731">Obligation: The NBFC remains responsible for the data privacy and security of borrower personal information, including data held by its LSPs. It must have clear policies on data storage and on standards for handling a security breach, disclosed on its website and DLA. It must also ensure that it and its LSPs comply with RBI cybersecurity standards.
Recommendation: Write a breach-handling standard, publish it on the website and DLA, and cover LSPs. Align the incident plan with RBI cybersecurity requirements, since the current plan has no regulator or board escalation. The passages provided do not state a specific RBI incident-reporting timeline.</finding>
<finding severity="LOW" cites="1718">Obligation: Digital lending must be covered by a Board-approved credit policy. A breach plan that excludes the board from oversight is inconsistent with this governance requirement.
Recommendation: Check that the Board-approved digital lending policy covers data security and breach escalation, and add a path to inform the board of breaches.</finding>
</findings>
<passages>
<passage id="1718" document="Reserve Bank of India (Non-Banking Financial Companies – Credit Facilities) Directions, 2025" ref="Para 5">5. An NBFC shall put in place Board approved credit policy covering, inter alia, the
areas specified below, to the extent such activities are undertaken by it. The
specific aspects to be addressed in this policy are detailed in the relevant
paragraphs of these Directions.
(1) Digital Lending including DLG
(2) Lending Against Gold and Silver Collateral
(3) Microfinance Loans
(4) Project Finance
(5) Demand / Call Loans
(6) Housing Finance</passage>
<passage id="1729" document="Reserve Bank of India (Non-Banking Financial Companies – Credit Facilities) Directions, 2025" ref="Para 14">14. Storage of data
(1) An NBFC shall ensure that LSP engaged by them do not store personal
information of borrower except some basic minimal data (viz., name, address,
contact details of the customer, etc.) that may be required to carry out their
operations or service within the scope of the NBFC-LSP agreement.
Responsibility regarding data privacy and security of the customer’s personal
information on an ongoing basis shall be that of the NBFC.
(2) An NBFC shall ensure that clear policy guidelines regarding the storage of
customer data including the type of data that can be stored, the length of time
for which data can be stored, restrictions on the use of data, data destruction
protocol, standards for handling security breach, etc., are put in place and also
disclosed by the NBFC and the LSP engaged by the NBFC prominently on
their website and DLA at all times.
(3) An NBFC shall ensure that no biometric data is stored / collected by the NBFC
and LSP, unless allowed under extant statutory guidelines.
(4) An NBFC shall ensure that all data is stored only in servers located within India,
while ensuring compliance with statutory obligations/ regulatory instructions.
Further, in case the data is processed outside India, the same shall be deleted
from servers outside India and brought back to India within 24 hours of
processing.</passage>
<passage id="1731" document="Reserve Bank of India (Non-Banking Financial Companies – Credit Facilities) Directions, 2025" ref="Para 16">16. Technology standards
An NBFC shall ensure that they and the LSPs engaged by them comply with
various technology standards/ requirements on cybersecurity stipulated by the
Reserve Bank and other relevant agencies, or as may be specified from time to
time, for undertaking digital lending.</passage>
<passage id="1965" document="Digital Personal Data Protection Rules, 2025" ref="Rule 6">6. Reasonable security safeguards. — (1) A Data Fiduciary shall protect personal data in its possession or
under its control, including in respect of any processing undertaken by it or on its behalf by a Data
Processor, by taking reasonable security safeguards to prevent personal data breach, which shall include, at
the minimum, —
(a) appropriate data security measures, such as securing of personal data through encryption,
obfuscation, masking or the use of virtual tokens mapped to that personal data;
(b) appropriate measures to control access to the computer resources used by such Data Fiduciary or
such a Data Processor, wherever applicable;
(c) visibility on the accessing of such personal data, through appropriate logs, monitoring and review,
for enabling detection of unauthorised access, its investigation and remediation to prevent
recurrence;
(d) reasonable measures for continued processing in the event of confidentiality, integrity or
availability of such personal data being compromised as a result of destruction or loss of access to
personal data or otherwise, such as by way of data-backups;
(e) for enabling the detection of unauthorised access, its investigation, remediation to prevent
recurrence and continued processing in the event of such a compromise, retain such logs and
personal data for a period of one year, unless compliance with any law for the time being in force
requires otherwise;
(f) appropriate provision in the contract entered into between such Data Fiduciary and such a Data
Processor, wherever applicable, for taking reasonable security safeguards; and
(g) appropriate technical and organisational measures to ensure effective observance of security
safeguards.
(2) In this rule, the expression “computer resource” shall have the same meaning as is assigned to it in
Information Technology Act, 2000 (21 of 2000).</passage>
<passage id="1966" document="Digital Personal Data Protection Rules, 2025" ref="Rule 7">7. Intimation of personal data breach. — (1) On becoming aware of any personal data breach, the Data
Fiduciary shall, to the best of its knowledge, intimate to each affected Data Principal, in a concise, clear and
plain manner and without delay, through her user account or any mode of communication registered by her
with the Data Fiduciary, —
(a) a description of the breach, including its nature, extent and the timing of its occurrence;
(b) the consequences relevant to her, that are likely to arise from the breach;
(c) the measures implemented and being implemented by the Data Fiduciary, if any, to mitigate risk;
(d) the safety measures that she may take to protect her interests; and
(e) business contact information of a person who is able to respond on behalf of the Data Fiduciary, to
queries, if any, of the Data Principal.
(2) On becoming aware of any personal data breach, the Data Fiduciary shall intimate to the Board, —
(a) without delay, a description of the breach, including its nature, extent, timing and location of
occurrence and the likely impact;
(b) within seventy-two hours of becoming aware of the breach, or within such longer period as the
Board may allow on a request made in writing in this behalf, —
(i) updated and detailed information in respect of such description;
(ii) the broad facts related to the events, circumstances and reasons leading to the breach;
(iii) measures implemented or proposed, if any, to mitigate risk;
(iv) any findings regarding the person who caused the breach;
(v) remedial measures taken to prevent recurrence of such breach; and
(vi) a report regarding the intimations given to affected Data Principals.</passage>
</passages>
```

## dpdp-children

```text
<feature>We are launching a pocket-money card and app for teenagers aged 13 to 17. They sign up themselves with their name, date of birth and phone number; parents are not involved.</feature>
<findings>
<finding severity="HIGH" cites="1970,1971">Obligation: A Data Fiduciary must adopt technical and organisational measures to obtain verifiable parental consent before processing any personal data of a child (under 18). A 13-17 year old cannot validly consent alone.
Recommendation: Redesign onboarding so a parent or guardian is identified and gives verifiable consent before any child data (name, date of birth, phone number) is processed. Do not allow self sign-up without this step.</finding>
<finding severity="HIGH" cites="1972,1971,1970">Obligation: The Data Fiduciary must check that the person claiming to be the parent is an identifiable adult. It does this using reliable identity and age details it already holds, or details voluntarily provided by the parent, including through a government-authorised entity's virtual token or a Digital Locker service provider.
Recommendation: Build a parent verification flow. For existing users, confirm the data held is reliable. For new parents, verify age and identity through government-issued details, a virtual token or DigiLocker before creating the child's account.</finding>
<finding severity="HIGH" cites="1576,1577">Obligation: When an NBFC establishes an account-based relationship, it must carry out CDD by obtaining Aadhaar or an OVD (or equivalent e-document, or KYC Identifier) and PAN or Form 60, and must verify these. Self-declared name, date of birth and phone number do not meet this. Minor-specific or guardian provisions are not stated in the passages given.
Recommendation: Confirm with compliance how KYC applies to minors and the guardian's role. Do not onboard minors on self-declared details alone. Obtain and verify the required identity documents, involving the guardian where the Directions require it.</finding>
<finding severity="HIGH" cites="1577,1592">Obligation: Verification must follow prescribed methods: offline verification of Aadhaar, digital signature verification of e-documents with a live photo, digital KYC, or CKYCR retrieval. A simplified procedure applies only where the person cannot produce the documents, and only under stated conditions.
Recommendation: Add an identity verification step (Aadhaar offline verification, OVD e-document, Digital KYC or V-CIP). Use the simplified procedure only if its conditions are met and documented.</finding>
<finding severity="MEDIUM" cites="1613">Obligation: Accounts opened non-face-to-face (a remote app sign-up) are subject to enhanced due diligence. Such customers are categorised as high-risk, and the first transaction must be a credit from the customer's existing KYC-compliant bank account.
Recommendation: Apply EDD controls to remote onboarding. Fund the first transaction from an existing KYC-compliant account, and treat these accounts as high-risk with enhanced monitoring.</finding>
<finding severity="MEDIUM" cites="2027,2022,2026">Obligation: The child-data protections in section 9 (parental consent, no tracking or behavioural monitoring) are relaxed only for the listed purposes, such as real-time location for safety, or preventing access to harmful content. A pocket-money app's usage tracking or ad targeting is not among them.
Recommendation: Do not track, behaviourally monitor or target advertising at child users. Limit any processing to what the Fourth Schedule exemptions allow, and document the basis.</finding>
<finding severity="MEDIUM" cites="1721,1722,2081">Obligation: If the card has any credit component, the NBFC must assess creditworthiness, including age, occupation and income, before extending a loan. It must also provide a Key Facts Statement with APR and all charges to the borrower. Credit card receivables are exempt from the KFS rules. The passages do not address capacity of minors.
Recommendation: Keep the product strictly prepaid or debit-like with no credit or overdraft for under-18s. If any credit or fee element is planned, obtain legal advice on contractual capacity, run the age, occupation and income assessment, and provide a KFS and clear charge disclosure.</finding>
</findings>
<passages>
<passage id="1576" document="Reserve Bank of India (Non-Banking Financial Companies – Know Your Customer) Directions, 2025" ref="Para 23, part 1 of 4">23. For undertaking CDD, the NBFC shall obtain the following from an individual
while establishing an account-based relationship or while dealing with the individual
who is a beneficial owner, authorised signatory or the power of attorney holder related
to any legal entity:
(1) the Aadhaar number where,
(i) they are desirous of receiving any benefit or subsidy under any scheme notified
under section 7 of the Aadhaar (Targeted Delivery of Financial and Other subsidies,
Benefits and Services) Act, 2016 (18 of 2016); or
(ii) they decide to submit their Aadhaar number voluntarily to a NBFC or any RE
notified under the first proviso to sub-section (1) of section 11A of the PML Act; or
(2) the proof of possession of Aadhaar number where the NBFC can carry out
offline verification; or
(3) the proof of possession of Aadhaar number where the NBFC cannot carry out
the offline verification or any OVD or the equivalent e-document thereof containing the
details of their identity and address; or
(4) the KYC Identifier with an explicit consent to download records from CKYCR;
and
(5) the PAN or the equivalent e-document thereof or Form No. 60 as defined in
Income-tax Rules, 1962; and
(6) the NBFC may require such other documents including in respect of the nature
of business and financial status of the customer, or the equivalent e-documents
thereof.
Provided that where the customer has submitted,
(i) Aadhaar number under clause (1) above to a NBFC notified under first proviso
to sub-section (1) of section 11A of the PML Act, such NBFC shall carry out
authentication of the customer’s Aadhaar number using UIDAI’s e-KYC authentication.
Further, in such a case, if the customer wants to provide a current address, different
from the address as per the identity information available in the Central Identities Data
Repository, they may give a self-declaration to that effect to the NBFC.</passage>
<passage id="1577" document="Reserve Bank of India (Non-Banking Financial Companies – Know Your Customer) Directions, 2025" ref="Para 23, part 2 of 4">23. For undertaking CDD, the NBFC shall obtain the following from an individual
(ii) proof of possession of Aadhaar under clause (2) above where offline verification
can be carried out, the NBFC shall carry out offline verification.
(iii) an equivalent e-document of any OVD, the NBFC shall verify the digital
signature as per the provisions of the Information Technology Act, 2000 (21 of 2000)
and any rules issued thereunder and take a live photo as specified under paragraph
24 below.
(iv) any OVD or proof of possession of Aadhaar number under clause (3) above
where offline verification cannot be carried out, the NBFC shall carry out verification
through digital KYC as specified under paragraph 24 below.</passage>
<passage id="1592" document="Reserve Bank of India (Non-Banking Financial Companies – Know Your Customer) Directions, 2025" ref="Para 28">28. Simplified procedure for opening accounts by NBFCs: In case a person who
desires to open an account is not able to produce documents, as specified in paragraph
23, NBFCs may at their discretion open accounts subject to the following conditions:
(i) The NBFC shall obtain a self-attested photograp</passage>
<passage id="1613" document="Reserve Bank of India (Non-Banking Financial Companies – Know Your Customer) Directions, 2025" ref="Para 44, part 2 of 2">44. Enhanced Due Diligence (EDD) for non-face-to-face customer onboarding
(5) First transaction in such accounts shall be a credit from existing KYC-complied
bank account of the customer.
(6) The NBFC shall categorise such customers as high-risk customers and shall
subject accounts opened in non-fac</passage>
<passage id="1721" document="Reserve Bank of India (Non-Banking Financial Companies – Credit Facilities) Directions, 2025" ref="Para 8">8. Assessing the borrower’s creditworthiness
(1) An NBFC shall obtain the necessary information relating to economic profile of
the borrower with a view to assessing the borrower’s creditworthiness before
extending any loan, including, at a minimum, age, occupation and income
details. The same shall be kept on record for audit purposes.
(2) An NBFC shall ensure that there is no automatic increase in credit limit unless
an explicit request is received, evaluated and kept on record from the borrower
for such increase.</passage>
<passage id="1722" document="Reserve Bank of India (Non-Banking Financial Companies – Credit Facilities) Directions, 2025" ref="Para 9, part 1 of 2">9. Disclosures to borrowers
(1) An NBFC shall provide a Key Fact Statement (KFS), as per instructions
contained in Reserve Bank of India (Non- Banking Financial Companies –
Responsible Business Conduct) Directions, 2025.
(2) As regards penal charges, an NBFC shall be guided by Reserve Bank of India
</passage>
<passage id="1970" document="Digital Personal Data Protection Rules, 2025" ref="Rule 10, part 1 of 3">10. Verifiable consent for processing of personal data of child.—(1) A Data Fiduciary shall adopt
appropriate technical and organisational measures to ensure that verifiable consent of the parent is obtained
before the processing of any personal data of a child and shall observe due diligence, for checking that the
individual identifying herself as the parent is an adult who is identifiable if required in connection with
compliance with any law for the time being in force in India, by reference to—
(a) reliable details of identity and age of the individual available with the Data Fiduciary; or
(b) details of identity and age, voluntarily provided —
(i) by the individual; or
(ii) through a virtual token mapped to such details, which is issued by an authorised entity.
(2) In this rule, the expression—
(a) “adult” shall mean an individual who has completed the age of eighteen years;
(b) “authorised entity" shall mean —
(i) an entity entrusted by law or by the Central Government or by the State Government with
the issuance of details of the identity and age or a virtual token mapped to such details; or
(ii) a person appointed or permitted by the entity specified under clause (i), for such issuance,
and also includes details of identity and age or token made available and verified by a Digital
Locker Service Provider;</passage>
<passage id="1971" document="Digital Personal Data Protection Rules, 2025" ref="Rule 10, part 2 of 3">10. Verifiable consent for processing of personal data of child.—(1) A Data Fiduciary shall adopt
(c) “Digital Locker service provider” shall mean such intermediary, including a body corporate or an
agency of the appropriate Government, as may be notified by the Central Government, in
accordance with the rules made in this regard under the Information Technology Act, 2000 (21 of
2000);
Illustration.
C is a child, P is a parent, and DF is a Data Fiduciary. A user account of C is sought to be created
on the online platform of DF, by processing the personal data of C.
Case 1: C informs DF that she is a child and declares P as her parent. DF shall enable P to identify
herself through its website, app or other appropriate means. P identifies herself as the parent and informs
DF that she is a registered user on DF’s platform and has previously made available her identity and age
details to DF. Before processing C’s personal data for the creation of her user account, DF shall check to
confirm that it holds reliable identity and age details of P and that P is an identifiable adult.
Case 2: C informs DF that she is a child and declares P as her parent. DF shall enable P to identify
herself through its website, app or other appropriate means. P identifies herself as the parent and informs
DF that she herself is not a registered user on DF’s platform. Before processing C’s personal data for the
creation of her user account, DF shall, by reference to identity and age details issued by an entity entrusted
by law or the Government with maintenance of the said details or to a virtual token mapped to the identity
and age, check that P is an identifiable adult. P may voluntarily make such details available using the
services of a Digital Locker service provider.
Case 3: P is opening an account for C and identifies herself as C’s parent and informs DF that she
is a registered user on DF’s platform and has previously made available her identity and age details to DF.</passage>
<passage id="1972" document="Digital Personal Data Protection Rules, 2025" ref="Rule 10, part 3 of 3">10. Verifiable consent for processing of personal data of child.—(1) A Data Fiduciary shall adopt
Before processing C’s personal data for the creation of her user account, DF shall check to confirm that it
holds reliable identity and age details of P and that P is an identifiable adult.
Case 4: P is opening an account for C and identifies herself as C’s parent and informs DF that she
herself is not a registered user on DF’s platform. Before processing C’s personal data for the creation of her
user account, DF shall, by reference to identity and age details issued by an entity entrusted by law or the
Government with maintenance of the said details or to a virtual token mapped to the identity and age, check
that P is an identifiable adult. P may voluntarily make such details available using the services of a Digital
Locker service provider.</passage>
<passage id="2022" document="Digital Personal Data Protection Rules, 2025" ref="Fourth Schedule, Part B">Purposes for which provisions of sub-sections (1) and (3) of section 9 shall not apply
S.
No. Purposes Conditions
(1) (2) (3)</passage>
<passage id="2026" document="Digital Personal Data Protection Rules, 2025" ref="Fourth Schedule, Part B, Item 4">4. For the determination of real-time location of
a child.
Processing is restricted to the tracking of real-time
location of such child, in the interest of her safety
and protection or security.</passage>
<passage id="2027" document="Digital Personal Data Protection Rules, 2025" ref="Fourth Schedule, Part B, Item 5">5. For ensuring that any information, service or
advertisement likely to cause any detrimental
effect on the well-being of a child is not
accessible to her.
Processing is restricted to the extent necessary to
ensure that such information, service or
advertisement is not accessible to the child.</passage>
<passage id="2081" document="Reserve Bank of India (Non-Banking Financial Companies – Responsible Business Conduct) Directions, 2025" ref="Para 29, part 1 of 3">29. The following instructions shall be applicable in case of all new retail and MSME
term loans sanctioned on or after October 1, 2024, including fresh loans to existing
customers, by an NBFC. Credit card receivables are exempted from the provisions
given below:
(1) An NBFC shall provide a KFS to all prospective borrowers to help them take an
informed view before executing the loan contract, as per the standardised format
given in the Annex I. The KFS shall be written in a language understood by such
borrowers. Contents of KFS shall be explained to the borrower and an
acknowledgement shall be obtained that they have understood the same.
(2) The KFS shall be provided with a unique proposal number and shall have a
validity period of at least three working days for loans having tenor of seven days
or more, and a validity period of one working day for loans having tenor of less than
seven days.
Explanation: Validity period refers to the period available to the borrower, after being
provided the KFS by the NBFC, to agree to the terms of the loan. The NBFC shall
be bound by the terms of the loan indicated in the KFS, if agreed to by the borrower
during the validity period.
(3) The KFS shall also include a computation sheet of Annual Percentage Rate
(APR), and the amortisation schedule of the loan over the loan tenor. APR will
include all charges which are levied by the NBFC. Illustrative examples of
calculation of APR and disclosure of repayment schedule for a hypothetical loan
are given below:</passage>
</passages>
```

## kyc-aadhaar-images

```text
<feature>During onboarding we photograph the customer's Aadhaar card (front and back) and keep the unmasked images in our cloud bucket indefinitely, so that periodic re-KYC can reuse them. Branch staff can download them from the admin portal.</feature>
<findings>
<finding severity="HIGH" cites="1579,1590">Obligation: Where Aadhaar authentication is not required, the NBFC must have the customer black out the Aadhaar number through appropriate means. The same redaction applies in V-CIP. Aadhaar use must also follow the Aadhaar Act and its regulations.
Recommendation: Stop storing unmasked Aadhaar images. Redact or black out the Aadhaar number at capture unless authentication is required, and mask existing stored images. Confirm the flow against the Aadhaar Act and regulations.</finding>
<finding severity="LOW" cites="1616">Obligation: Records of customer identification and address must be kept for at least five years after the business relationship has ended. Transaction records must be kept for at least five years from the date of the transaction.
Recommendation: Replace the indefinite retention with a defined schedule that runs five years from the end of the business relationship. Keep only the records required (for example, masked copies) and delete them after that period.</finding>
<finding severity="MEDIUM" cites="1968,1616">Obligation: A Data Fiduciary must retain personal data and processing logs for a minimum of one year and then erase them, unless another law requires longer retention. Indefinite retention of unmasked Aadhaar images has no basis beyond the legal retention requirement.
Recommendation: Define a retention and erasure policy that ties retention to the KYC record-keeping period. Erase the images and logs once that period ends, and do not keep them indefinitely.</finding>
<finding severity="MEDIUM" cites="1965">Obligation: The Data Fiduciary must take reasonable security safeguards, at a minimum: encryption, obfuscation or masking; access controls; logs, monitoring and review of access to personal data; backups; one-year log retention; and contractual safeguards with processors.
Recommendation: Encrypt the cloud bucket and restrict access by role. Disable bulk or branch-level downloads unless they are necessary. Log and review every access to Aadhaar images and keep the logs for at least one year. Ensure the cloud provider contract carries security obligations.</finding>
<finding severity="MEDIUM" cites="1606,1607,1608">Obligation: Periodic KYC updation is risk-based (2, 8 or 10 years). For individuals with no change, a self-declaration suffices. Where documents are not as per current CDD standards, or have expired, fresh KYC is required. Aadhaar OTP e-KYC may be used, and the NBFC must update records and acknowledge the customer.
Recommendation: Do not rely on stored Aadhaar images for re-KYC. Use self-declaration, Aadhaar OTP e-KYC or other permitted modes, and do fresh KYC where documents are expired or non-compliant. Document the approach in the Board-approved KYC policy.</finding>
</findings>
<passages>
<passage id="1579" document="Reserve Bank of India (Non-Banking Financial Companies – Know Your Customer) Directions, 2025" ref="Para 23, part 4 of 4">23. For undertaking CDD, the NBFC shall obtain the following from an individual
blacks out his Aadhaar number through appropriate means where the authentication
of Aadhaar number is not required as per proviso (i) above.
Explanation 2: An NBFC official can perform biometric-based e-KYC authentication,
including Aadhaar Face Authentication.
Explanation 3: The NBFC shall ensure that the use of Aadhaar, proof of possession of
Aadhaar etc., is in accordance with the Aadhaar (Targeted Delivery of Financial and
Other Subsidies Benefits and Services) Act, 2016 and the regulations made
thereunder.
Explanation 4: Aadhaar number is not mandatory for purposes of KYC. However, in
case the customer is desirous of receiving any benefit or subsidy under any scheme
notified under section 7 of the Aadhaar (Targeted Delivery of Financial and Other
subsidies, Benefits and Services) Act, 2016 (18 of 2016), the customer shall provide
the Aadhaar number to the NBFC. In other cases, customers may provide the Aadhaar
number voluntarily.</passage>
<passage id="1590" document="Reserve Bank of India (Non-Banking Financial Companies – Know Your Customer) Directions, 2025" ref="Para 27, part 4 of 5">27. The NBFC opting to undertake V-CIP, shall adhere to the following
(d) Equivalent e-document of Officially Valid Documents (OVDs) including
documents issued through DigiLocker.
(vii) The NBFC shall ensure to redact or blackout the Aadhaar number in terms of
paragraph 23.
(viii) In case of offline</passage>
<passage id="1606" document="Reserve Bank of India (Non-Banking Financial Companies – Know Your Customer) Directions, 2025" ref="Para 42, part 1 of 5">42. Updation / Periodic Updation of KYC
(1) The NBFC shall adopt a risk-based approach for periodic updation of KYC
ensuring that it keeps the information or data collected under CDD is kept up-to-date
and relevant, particularly where there is high risk. However, the NBFC shall carry out
periodic updation at least once in every two years for high-risk customers, once in
every eight years for medium risk customers and once in every 10 years for low-risk
customers from the date of opening of the account / last KYC updation. The NBFC
shall document its policy in this regard as part of the NBFC’s internal KYC policy duly
approved by the Board of Directors of NBFC or any committee of the Board to which
power has been delegated.
(2) Notwithstanding the provisions given above, in respect of an individual
customer who is categorised as low-risk, the NBFC shall allow all transactions and
ensure the updation of KYC within one year of its falling due for KYC or up to June 30,
2026, whichever is later. The NBFC shall subject accounts of such customers to
regular monitoring. This shall also apply to low-risk individual customers for whom
periodic updation of KYC has already fallen due.
(3) Individuals:
(i) No change in KYC information: In case of no change in the KYC information,
the NBFC shall obtain a self-declaration from the customer in this regard through the
customer’s email-id registered with the NBFC, customer’s mobile number registered
with the NBFC, digital channels (including mobile application of NBFC) letter, etc.</passage>
<passage id="1607" document="Reserve Bank of India (Non-Banking Financial Companies – Know Your Customer) Directions, 2025" ref="Para 42, part 2 of 5">42. Updation / Periodic Updation of KYC
(ii) Change in address: In case of a change only in the address details of the
customer, the NBFC shall obtain a self-declaration of the new address from the
customer through customer’s email-id registered with the NBFC, customer’s mobile
number registered with the NBFC, ATMs, digital channels (including mobile application
of NBFC), letter, etc., and shall verify the declared address through positive
confirmation within two months, by means such as address verification letter, contact
point verification, deliverables, etc.
(iii) Further, the NBFC at its option, may obtain a copy of OVD or deemed OVD, as
defined in sub-clause (xiv) of clause (1) of paragraph 5 or the equivalent e-documents
thereof, as defined in sub-clause (x) of clause (1) of paragraph 5 for the purpose of
proof of address, declared by the customer at the time of updation / periodic updation.
However, the NBFC shall clearly specify such requirement, in its internal KYC policy
duly approved by the Board of Directors of the NBFC or any committee of the Board
to which power has been delegated.
(iv) Accounts of customers, who were minor at the time of opening account, on their
becoming major: In case of customers for whom the NBFC opened an account when
they were minors, the NBFC shall obtain fresh photographs upon their becoming a
major and, at that time, shall ensure that CDD documents as per the current CDD
standards are available. Wherever required, the NBFC may carry out fresh KYC of
such customers, i.e., customers for whom it opened account when they were minor,
upon their becoming a major.
(v) The NBFC may use Aadhaar OTP based e-KYC in non-face-to-face mode for
updation / periodic updation. To clarify, conditions stipulated in paragraph 25 are not
applicable in case of updation / periodic updation of KYC through Aadhaar OTP based
e-KYC in non-face to face mode.</passage>
<passage id="1608" document="Reserve Bank of India (Non-Banking Financial Companies – Know Your Customer) Directions, 2025" ref="Para 42, part 3 of 5">42. Updation / Periodic Updation of KYC
(vi) Declaration of current address, if the current address is different from the
address in Aadhaar, shall not require positive confirmation in this case. The NBFC
shall ensure that the mobile number for Aadhaar authentication is same as the one
available with them in the customer’s profile, in order to prevent any fraud.
(4) Customers other than individuals:
(i) No change in KYC information: In case of no change in the KYC information
of the LE customer, the NBFC shall obtain a self-declaration in this regard from the LE
customer through its email id registered with the NBFC, ATMs, digital channels
(including mobile application of NBFC), letter from an official authorised by the LE in
this regard, board resolution, etc. Further, the NBFC shall ensure during this process
that Beneficial Ownership (BO) information available with them is accurate and shall
update the same, if required, to keep it as up-to-date as possible.
(ii) Change in KYC information: In case of change in KYC information, the NBFC
shall undertake the KYC process equivalent to that applicable for onboarding a new
LE customer.
(5) Additional measures: In addition to the above, the NBFC shall ensure that:
(i) The NBFC has customer’s KYC document as per the current CDD standards
available with it. This is applicable even if there is no change in customer information
but the documents available with the NBFC are not as per the current CDD standards.
Further, in case the validity of the CDD documents available with the NBFC has
expired at the time of periodic updation of KYC, the NBFC shall undertake the KYC
process equivalent to that applicable for onboarding a new customer.
(ii) The NBFC verifies the Customer’s PAN details, if available, from the database
of the issuing authority at the time of periodic updation of KYC.</passage>
<passage id="1616" document="Reserve Bank of India (Non-Banking Financial Companies – Know Your Customer) Directions, 2025" ref="Para 47">47. The NBFC shall take the following steps regarding maintenance,
preservation and reporting of customer information, with reference to provisions of
PML Act and Rules. The NBFC shall,
(1) maintain all necessary records of transactions between the NBFC and the
customer, both domestic and international, for at least five years from the date of
transaction;
(2) preserve the records pertaining to the identification of the customers and their
addresses, obtained while opening the account and during the course of business
relationship, for at least five years after the business relationship has ended;
(3) swiftly make available, the identification records and transaction data to the
competent authorities upon request;
(4) introduce a system of maintaining proper records of transactions prescribed
under Rule 3 of Prevention of Money Laundering (Maintenance of Records) Rules,
2005 (PML Rules, 2005);
(5) maintain all necessary information in respect of transactions prescribed under
PML Rule 3 to permit the reconstruction of an individual transaction, including the
following:
(i) the nature of the transactions;
(ii) the amount of the transaction and the currency in which it was denominated;
(iii) the date on which the transaction was conducted; and
(iv) the parties to the transaction.
(6) evolve a system for proper maintenance and preservation of account
information in a manner that allows the NBFC to retrieve data easily and quickly
whenever required or when competent authorities request it;
(7) maintain records of the identity and address of its customers, and records in
respect of transactions referred to in Rule 3 in hard or soft format.
Explanation: For the purpose of this paragraph, the expressions ‘records
pertaining to the identification’, ‘identification records’, etc., shall include
updated records of the identification data, account files, business correspondence,
and results of any analysis undertaken.</passage>
<passage id="1965" document="Digital Personal Data Protection Rules, 2025" ref="Rule 6">6. Reasonable security safeguards. — (1) A Data Fiduciary shall protect personal data in its possession or
under its control, including in respect of any processing undertaken by it or on its behalf by a Data
Processor, by taking reasonable security safeguards to prevent personal data breach, which shall include, at
the minimum, —
(a) appropriate data security measures, such as securing of personal data through encryption,
obfuscation, masking or the use of virtual tokens mapped to that personal data;
(b) appropriate measures to control access to the computer resources used by such Data Fiduciary or
such a Data Processor, wherever applicable;
(c) visibility on the accessing of such personal data, through appropriate logs, monitoring and review,
for enabling detection of unauthorised access, its investigation and remediation to prevent
recurrence;
(d) reasonable measures for continued processing in the event of confidentiality, integrity or
availability of such personal data being compromised as a result of destruction or loss of access to
personal data or otherwise, such as by way of data-backups;
(e) for enabling the detection of unauthorised access, its investigation, remediation to prevent
recurrence and continued processing in the event of such a compromise, retain such logs and
personal data for a period of one year, unless compliance with any law for the time being in force
requires otherwise;
(f) appropriate provision in the contract entered into between such Data Fiduciary and such a Data
Processor, wherever applicable, for taking reasonable security safeguards; and
(g) appropriate technical and organisational measures to ensure effective observance of security
safeguards.
(2) In this rule, the expression “computer resource” shall have the same meaning as is assigned to it in
Information Technology Act, 2000 (21 of 2000).</passage>
<passage id="1968" document="Digital Personal Data Protection Rules, 2025" ref="Rule 8, part 2 of 2">8. Time period for specified purpose to be deemed as no longer being served.—(1) A Data Fiduciary,
(3) Without prejudice to sub-rules (1) and (2), a Data Fiduciary shall retain, in respect of any processing of
personal data undertaken by it or on its behalf by a Data Processor, such personal data, associated traffic
data and other logs of the processing for a minimum period of one year from the date of such processing,
for the purposes as specified in the Seventh Schedule, after which the Data Fiduciary shall cause such
personal data and logs to be erased, unless further retention is required for compliance with any other law
for the time being in force or notified by the Government.
Illustration.
Case 1: X, a Data Principal purchases an e-book on an e-book platform Y. Once delivery is
completed, the specified purpose of processing is served. The platform Y must retain the order details,
personal data, and logs of the processing (such as order confirmation, payment, and delivery events) for at
least one year from the date of the transaction, even if X deletes her account.
Case 2: X, a company engages a cloud service provider C as its Data Processor to host customer
records. X as the Data Fiduciary, is required to ensure that the C also retains the data and associated logs
for at least one year before erasure, unless any other applicable law requires a longer period.</passage>
</passages>
```

## kyc-no-periodic-update

```text
<feature>We complete KYC once at onboarding and never update it afterwards, including for customers our risk engine classifies as high risk.</feature>
<findings>
<finding severity="HIGH" cites="1606">Obligation: The NBFC must carry out periodic KYC updation at least once every two years for high-risk customers, every eight years for medium-risk and every ten years for low-risk customers, counted from account opening or last updation. The policy must be documented in the Board-approved KYC policy.
Recommendation: Build periodic KYC updation into the product with a two-year cycle for high-risk, eight-year for medium-risk and ten-year for low-risk customers. Document it in the Board-approved KYC policy. Identify and remediate existing customers whose updation is overdue.</finding>
<finding severity="HIGH" cites="1605,1603">Obligation: The NBFC must align monitoring with each customer's risk category and subject high-risk accounts to more intensified monitoring. It must also review risk categorisation at least every six months and decide whether enhanced due diligence is needed.
Recommendation: Put in place a periodic risk-categorisation review at least every six months. Trigger enhanced due diligence and intensified monitoring for high-risk customers, and make sure ongoing due diligence checks transactions against the customer's profile and source of funds.</finding>
<finding severity="MEDIUM" cites="1609,1606,1607">Obligation: For updation, the NBFC must obtain a self-declaration where nothing has changed, verify a changed address within two months, and ensure KYC documents meet current CDD standards. It must also acknowledge receipt of documents, promptly update its records, and intimate the customer of the date of updation.
Recommendation: Build updation workflows covering no-change self-declaration, change of address with verification within two months, acknowledgment and customer intimation, and re-KYC when documents are outdated or expired. Document these in the Board-approved policy.</finding>
<finding severity="MEDIUM" cites="1574,1605">Obligation: The NBFC must review risk categorisation at least every six months. It must also carry out identification afresh when there is doubt about the authenticity or adequacy of previously obtained customer identification data.
Recommendation: Add event-based triggers for re-identification, such as doubts about the authenticity or adequacy of KYC data, alongside the scheduled six-monthly risk review. Feed the results back into the customer's risk category.</finding>
</findings>
<passages>
<passage id="1574" document="Reserve Bank of India (Non-Banking Financial Companies – Know Your Customer) Directions, 2025" ref="Para 21">21. The NBFC shall undertake identification of customers in the following cases:
(1) Commencement of an account-based relationship with the customer.
(2) Carrying out any international money transfer operations for a person who is
not an account holder of the NBFC.
(3) When there is a doubt about the authenticity or adequacy of the customer
identification data it has obtained.
(4) Selling third-party products as agents, selling its own products, payment of
dues of credit cards / sale and reloading of prepaid / travel cards and any other
product for more than ₹50,000.
(5) Carrying out transactions for a non-account-based customer, i.e., a walk-in
customer, where the amount involved is equal to or exceeds ₹50,000 whether
conducted as a single transaction or several transactions that appear to be connected.
(6) When the NBFC has reason to believe that a customer (account-based or walk-
in) is intentionally structuring a transaction into a series of transactions below the
threshold of ₹50,000.
(7) The NBFC shall ensure it does not seek introductions while opening accounts.</passage>
<passage id="1603" document="Reserve Bank of India (Non-Banking Financial Companies – Know Your Customer) Directions, 2025" ref="Para 39">39. The NBFC shall undertake ongoing due diligence of customers to ensure that
their transactions are consistent with their knowledge about the customers, customers’
business and risk profile, the source of funds / wealth.</passage>
<passage id="1605" document="Reserve Bank of India (Non-Banking Financial Companies – Know Your Customer) Directions, 2025" ref="Para 41">41. The NBFC shall align the extent of monitoring with the risk category of the
customer.
(1) The NBFC shall put in place a system of periodic review of risk categorisation
of accounts, with such periodicity being at least once in every six months and shall
establish the need for applying enhanced due diligence measures.
(2) The NBFC shall closely monitor the transactions in accounts of marketing firms,
especially accounts of Multi-level Marketing (MLM) companies.
Explanation: The NBFC shall subject high-risk accounts to more intensified
monitoring.</passage>
<passage id="1606" document="Reserve Bank of India (Non-Banking Financial Companies – Know Your Customer) Directions, 2025" ref="Para 42, part 1 of 5">42. Updation / Periodic Updation of KYC
(1) The NBFC shall adopt a risk-based approach for periodic updation of KYC
ensuring that it keeps the information or data collected under CDD is kept up-to-date
and relevant, particularly where there is high risk. However, the NBFC shall carry out
periodic updation at least once in every two years for high-risk customers, once in
every eight years for medium risk customers and once in every 10 years for low-risk
customers from the date of opening of the account / last KYC updation. The NBFC
shall document its policy in this regard as part of the NBFC’s internal KYC policy duly
approved by the Board of Directors of NBFC or any committee of the Board to which
power has been delegated.
(2) Notwithstanding the provisions given above, in respect of an individual
customer who is categorised as low-risk, the NBFC shall allow all transactions and
ensure the updation of KYC within one year of its falling due for KYC or up to June 30,
2026, whichever is later. The NBFC shall subject accounts of such customers to
regular monitoring. This shall also apply to low-risk individual customers for whom
periodic updation of KYC has already fallen due.
(3) Individuals:
(i) No change in KYC information: In case of no change in the KYC information,
the NBFC shall obtain a self-declaration from the customer in this regard through the
customer’s email-id registered with the NBFC, customer’s mobile number registered
with the NBFC, digital channels (including mobile application of NBFC) letter, etc.</passage>
<passage id="1607" document="Reserve Bank of India (Non-Banking Financial Companies – Know Your Customer) Directions, 2025" ref="Para 42, part 2 of 5">42. Updation / Periodic Updation of KYC
(ii) Change in address: In case of a change only in the address details of the
customer, the NBFC shall obtain a self-declaration of the new address from the
customer through customer’s email-id registered with the NBFC, customer’s mobile
number registered with the NBFC, ATMs, digital channels (including mobile application
of NBFC), letter, etc., and shall verify the declared address through positive
confirmation within two months, by means such as address verification letter, contact
point verification, deliverables, etc.
(iii) Further, the NBFC at its option, may obtain a copy of OVD or deemed OVD, as
defined in sub-clause (xiv) of clause (1) of paragraph 5 or the equivalent e-documents
thereof, as defined in sub-clause (x) of clause (1) of paragraph 5 for the purpose of
proof of address, declared by the customer at the time of updation / periodic updation.
However, the NBFC shall clearly specify such requirement, in its internal KYC policy
duly approved by the Board of Directors of the NBFC or any committee of the Board
to which power has been delegated.
(iv) Accounts of customers, who were minor at the time of opening account, on their
becoming major: In case of customers for whom the NBFC opened an account when
they were minors, the NBFC shall obtain fresh photographs upon their becoming a
major and, at that time, shall ensure that CDD documents as per the current CDD
standards are available. Wherever required, the NBFC may carry out fresh KYC of
such customers, i.e., customers for whom it opened account when they were minor,
upon their becoming a major.
(v) The NBFC may use Aadhaar OTP based e-KYC in non-face-to-face mode for
updation / periodic updation. To clarify, conditions stipulated in paragraph 25 are not
applicable in case of updation / periodic updation of KYC through Aadhaar OTP based
e-KYC in non-face to face mode.</passage>
<passage id="1609" document="Reserve Bank of India (Non-Banking Financial Companies – Know Your Customer) Directions, 2025" ref="Para 42, part 4 of 5">42. Updation / Periodic Updation of KYC
(iii) The NBFC provides an acknowledgment to the customer mentioning the date
of receipt of the relevant document(s), including self-declaration from the customer,
for carrying out updation / periodic updation. Further, the NBFC shall ensure that it
promptly updates the information / documents obtained from the customers at the time
of updation / periodic updation of KYC in its records / database and provide an
intimation, mentioning the date of updation of KYC details, to the customer.
(iv) In order to ensure customer convenience, the NBFC may consider making
available the facility of updation / periodic updation of KYC at any branch, in terms of
their internal KYC policy duly approved by the Board of Directors of the NBFC or any
committee of the Board to which power has been delegated.
(v) The NBFC shall adopt a risk-based approach with respect to periodic updation
of KYC. The NBFC shall clearly specify in its internal policy, duly approved by the
Board of Directors of the NBFC or any committee of the Board to which power has
been delegated, any additional and exceptional measures, it adopts that are not
otherwise mandated under the above instructions, such as requirement of obtaining
recent photograph, requirement of physical presence of the customer, requirement of
periodic updation of KYC only in the branch of the NBFC where account is maintained,
a more frequent periodicity of KYC updation than the minimum specified periodicity
etc.</passage>
</passages>
```

## oos-dark-mode

```text
<feature>We are adding a dark mode toggle and a larger font option to the settings screen of our app. The choice is stored on the device only.</feature>
<findings>
(none)
</findings>
<passages>
(none)
</passages>
```

## oos-office-seating

```text
<feature>An internal tool lets our head-office employees book desks and meeting rooms for the week. Bookings are anonymous: the tool stores and shows only the room name and the time slot, never an employee name, ID or any other personal data.</feature>
<findings>
(none)
</findings>
<passages>
(none)
</passages>
```

## Labels

| Scenario | grounded | actionable | Note |
|----------|----------|------------|------|
| cf-contacts | 4 | 5 | Finding 4 infers that contacts got no notice; Rule 3's text doesn't say that. Rest exact |
| cf-data-abroad | 5 | 5 | Para 14(4) incl. 24-hour return; every finding matches its passage |
| cf-disbursal-via-lsp | 5 | 5 | Para 10(1)-(4), Para 6, Para 29 APR illustration all exact |
| cf-no-cooling-off | 5 | 5 | Para 11 exact; prepayment findings hedged correctly (loan type unknown) |
| dpdp-breach-notice | 4 | 4 | Rule 7/6 exact; LOW finding reads the Data Protection Board as the company board and cites Para 5 (credit policy) |
| dpdp-children | 4 | 4 | Rule 10 and KYC findings supported; Fourth Schedule finding claims more about s.9 than the cited items say; some generic advice |
| kyc-aadhaar-images | 5 | 5 | Para 23 blackout, Para 27, Para 47, Rule 8(3), Rule 6, Para 42 all match |
| kyc-no-periodic-update | 5 | 5 | Para 42(1) 2/8/10 years, Paras 39, 41, 21(3) exact |
| oos-dark-mode | 5 | 5 | No findings is right |
| oos-office-seating | 5 | 5 | No findings is right (scenario v2, anonymous bookings) |
