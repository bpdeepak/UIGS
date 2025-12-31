

# **1\. The Existing Research Landscape (What Has Been Done)**

Across all your papers, the literature clusters into **four major themes**:

---

## **A. Traditional → SSI Evolution (Identity Control)**

### **Key Works**

* *Shehu et al.* — GDPR compliance of SSI  
* *Mazzocca et al.* — Survey on DIDs & VCs

### **What They Solve**

* Show why **centralized and federated identity models are broken**  
* Define **SSI primitives**:  
  * DIDs  
  * Verifiable Credentials (VCs)  
  * Wallets  
  * Issuers / Holders / Verifiers  
* Analyze **regulatory compliance** (GDPR, eIDAS, EU Digital Identity)

### **Core Assumption (Critical)**

*Identity is a set of credentials that can be independently issued and verified.*

### **Limitation**

* Identity is treated as **static credentials**, not as a **long-lived, evolving entity**  
* No notion of:  
  * Identity continuity across time  
  * Identity drift  
  * Cross-domain identity composition

➡ **Fragmentation is reduced, not resolved**

---

## **B. Trust, Threat Models, and Security in SSI**

### **Key Works**

* *Krul et al.* — SoK: Trusting SSI  
* *Hardman*, *Ernstberger*, others referenced therein

### **What They Solve**

* Formalize **trust assumptions** in SSI  
* Identify **threat actors**:  
  * Issuers  
  * Wallets  
  * Verifiers  
  * Registries  
* Propose **trust models**:  
  * Minimal trust  
  * Extended trust  
  * Adversarial trust

### **Core Assumption**

*If trust is well-defined at each component boundary, the system is secure.*

### **Limitation**

* Trust is modeled **component-wise**, not **identity-wise**  
* No mechanism to:  
  * Correlate multiple identities belonging to the same human  
  * Reason about trust decay or accumulation over time  
* User is treated as a **passive holder**, not an active identity manager

➡ Trust ≠ Identity coherence

---

## **C. DID / VC Implementations & Infrastructure**

### **Key Works**

* Hyperledger Aries  
* DIDKit  
* Microsoft Entra Wallet  
* IOTA Identity  
  (covered extensively in )

### **What They Solve**

* Credential issuance & verification  
* Cryptographic soundness  
* Interoperability via W3C standards

### **Core Assumption**

*Correct primitives \+ standards \= usable identity system*

### **Limitation**

* Wallets become **credential dumps**  
* No system answers:  
  * “Which of my identities are linked?”  
  * “What does platform A know about me vs platform B?”  
  * “How has my identity evolved over 5 years?”

➡ Infrastructure exists, **identity reasoning does not**

---

## **D. Compliance, Privacy, and Regulation**

### **Key Works**

* GDPR compliance analyses (Shehu et al.)  
* EU Digital Identity Framework (reviewed in )

### **What They Solve**

* Consent  
* Revocation  
* Right to be forgotten (partially)  
* Data minimization

### **Core Assumption**

*If credentials are revocable and selective disclosure is used, privacy is solved.*

### **Limitation**

* Revocation ≠ erasure of **identity traces**  
* No accounting for:  
  * Historical identity exposure  
  * Cross-platform inference  
  * Identity correlation leakage

➡ Legal compliance ≠ identity sovereignty

---

# **2\. What Is Fundamentally Missing (Research Gaps)**

Now the **important part**.

Across *all* surveyed literature:

**NO system models identity as a unified, evolving, cross-platform entity.**

Let’s formalize the gaps.

---

## **GAP 1: No Model of Identity Continuity**

All systems assume:

* Identities are **issued**  
* Credentials are **presented**  
* Done.

What is missing:

* Identity before issuance  
* Identity after revocation  
* Identity evolution (education → employment → healthcare)

📌 **There is no temporal identity model**

---

## **GAP 2: No Representation of Identity Fragmentation Itself**

Ironically:

* SSI reduces reliance on IdPs  
* But **still does not unify identities**

Each DID:

* Exists independently  
* Has no formal relationship with other DIDs of the same person

📌 Fragmentation is acknowledged but **not computationally represented**

---

## **GAP 3: Wallet ≠ Identity Management System**

Wallets today:

* Store credentials  
* Do not reason over them

Missing capabilities:

* Identity graph  
* Exposure audit  
* Cross-domain correlation awareness

📌 Wallets are *storage*, not *identity intelligence systems*

---

## **GAP 4: No User-Centric Identity Reasoning**

Users cannot answer:

* “What does the internet know about me?”  
* “Which credentials jointly deanonymize me?”  
* “What identity subset should I expose?”

📌 No identity introspection layer exists

---

## **GAP 5: No Unified View Across Domains**

Healthcare identity ≠ Finance identity ≠ Education identity

But:

* Real humans are single entities

📌 No system integrates **domain-specific identities into a coherent whole**

---

# **3\. Why This Is NOT a “Solved Problem”**

Even the most advanced SSI systems **optimize verification**, not **identity modeling**.

This is why:

* Governments still issue siloed digital IDs  
* Big tech still controls identity graphs implicitly  
* Users remain powerless

Your intuition that “decision/prediction systems are dead ends” is **correct** — this is a **systems abstraction problem**, not an ML one.

---

# **4\. Where Your Project Can Be GENUINELY Novel**

Based on the literature gaps, a **strong major project contribution** would be:

---

## **🔹 Core Research Contribution (High Quality)**

**A Unified Identity Graph System that models fragmented digital identities as a single, evolving, privacy-preserving entity.**

### **Key Novelty**

* Identity is a **graph**, not a credential list  
* Identity evolves over time  
* Fragmentation is explicitly represented, not hidden

---

## **🔹 What You Build (System-Level)**

1. **Identity Graph Layer**  
   * Nodes: credentials, platforms, roles, attributes  
   * Edges: derivation, trust, correlation, exposure  
2. **Continuity Model**  
   * Temporal identity transitions  
   * Credential lifecycle tracking  
3. **Privacy-Preserving Linking**  
   * Zero-knowledge or consent-based correlation  
   * No central authority  
4. **User Introspection Interface**  
   * “What do I expose where?”  
   * “Which identities are linked?”  
   * “Risk of correlation”

---

## **🔹 Why This Is Novel (Compared to Literature)**

| Aspect | Existing Work | Your System |
| ----- | ----- | ----- |
| SSI primitives | ✔ | ✔ |
| Trust models | ✔ | ✔ |
| Credential security | ✔ | ✔ |
| Identity continuity | ❌ | ✔ |
| Fragmentation modeling | ❌ | ✔ |
| User identity reasoning | ❌ | ✔ |
| Cross-domain unification | ❌ | ✔ |

---