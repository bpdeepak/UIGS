

## **1\. Why Digital Identity Fragmentation Exists (Root Cause Analysis)**

Digital identity fragmentation is **not accidental**. It is the result of how systems evolved.

### **Historical reality**

* Early systems were **standalone** (bank DB, hospital DB, university DB)  
* Identity was introduced as a **local primary key**  
* Interoperability was never a design goal

Each system optimized for:

* Its own threat model  
* Its own schema  
* Its own business incentives

Result:

Identity ≠ Person  
Identity \= Account-in-a-System

This mismatch is the fundamental flaw.

---

## **2\. Why Existing “Identity Solutions” Fail**

Before proposing anything, you **must** understand why the obvious answers are wrong.

### **❌ Centralized Identity Providers (Google, Aadhaar, SSO)**

**Why they fail conceptually**

* They *replace* fragmentation with **central dependency**  
* Identity becomes:  
  * Revocable  
  * Censorable  
  * Jurisdiction-bound

They do **authentication**, not identity modeling.

They answer: “Are you allowed in?”  
Not: “Who are you across time and systems?”

---

### **❌ Blockchain / DID / Web3 Identity (as commonly proposed)**

**Why most DID systems fail**

* Assume a *single root identifier*  
* Ignore identity evolution  
* Do not model:  
  * Compromise  
  * Contextual roles  
  * Partial disclosure  
  * Historical continuity

Most DID systems are:

Cryptographic key management tools  
Not identity systems

---

### **❌ Data Portability / GDPR Exports**

**Why this is insufficient**

* Data is exported as **flat files**  
* No semantics  
* No continuity  
* No relationship between identities

You get *data*, not *identity structure*.

---

## **3\. Precise Reframing of the Problem (This Is Crucial)**

Let us restate the problem *correctly*.

### **What identity is NOT**

* Not a username  
* Not a login  
* Not a keypair  
* Not a government ID

### **What identity actually is**

**A time-evolving set of claims, credentials, roles, and interactions, distributed across independent systems, partially overlapping, partially conflicting.**

So the real problem becomes:

**How do we represent identity as a distributed, evolving graph of evidence — rather than a static identifier?**

This reframing is equivalent in quality to:

* Persona as node instead of label  
* Classification → link prediction

You are doing the **same level of abstraction shift**.

---

## **4\. Formal System Requirements (Non-Negotiable)**

A serious system must satisfy **all** of these:

### **R1. No Central Authority**

* No single entity controls identity resolution  
* Systems remain autonomous

### **R2. Partial Linkability**

* Some identities can be linked  
* Some must remain unlinkable  
* User controls granularity

### **R3. Temporal Continuity**

* Identity survives:  
  * Email changes  
  * Phone number changes  
  * Account deletion  
* History matters

### **R4. Privacy by Construction**

* No global correlation by default  
* Proof \> disclosure

### **R5. Auditability**

* User can answer:  
  * “Where does my data exist?”  
  * “What identity fragments exist?”  
  * “Which systems rely on which claims?”

If your system cannot satisfy these, it is not solving the problem.

---

## **5\. Core Technical Challenges (These Are the Real Hard Parts)**

This is where your project gains **academic weight**.

### **Challenge 1: Identity Without a Global Identifier**

You cannot assume:

* Aadhaar  
* Email  
* Phone number  
* Wallet address

You must model **identity resolution probabilistically or structurally**, not via IDs.

---

### **Challenge 2: Conflicting Identity Evidence**

Example:

* Two systems claim different DOB  
* Two emails linked to same phone historically  
* Name variations

The system must **represent conflict**, not overwrite truth.

---

### **Challenge 3: Identity Evolution Over Time**

Identities:

* Split (work vs personal)  
* Merge (marriage, migration)  
* Decay (abandoned accounts)

Most systems cannot represent this *at all*.

---

### **Challenge 4: Proof Without Disclosure**

“How do I prove I am over 18 **without revealing DOB or identity linkage**?”

This requires:

* Cryptographic proofs  
* Contextual claims  
* Scoped verification

---

## **6\. A Clean System Abstraction You Can Build**

Here is a **precise, implementable abstraction** suitable for a major project.

### **Core Idea: Identity as an Evolving Graph of Claims**

#### **Nodes**

* **Identity Fragment**  
  * A local account in a system  
* **Claim**  
  * “Age \> 18”  
  * “Degree from X”  
  * “Resident of Y”  
* **Credential**  
  * Signed attestations  
* **User-Controlled Anchor**  
  * Optional root of trust (not global)

#### **Edges**

* “Supports”  
* “Contradicts”  
* “Derived-from”  
* “Revoked-by”  
* “Temporal-successor”

#### **Properties**

* Time-stamped  
* Scoped  
* Cryptographically verifiable

This is **not a social graph**.  
This is an **identity evidence graph**.

---

### **System Capabilities**

Your system should allow:

1. **Local identity ingestion**  
   * Import accounts from multiple platforms  
2. **Claim extraction**  
   * Convert raw data into structured claims  
3. **User-mediated linking**  
   * Explicit or implicit linkage  
4. **Selective disclosure**  
   * Prove claims without exposing graph  
5. **Audit queries**  
   * “Show all systems relying on claim X”

---

## **7\. Why This Is IIT / KDD Level in Quality**

Let us be explicit.

| Criterion | This Problem |
| ----- | ----- |
| Real-world relevance | Extremely high |
| Exists independent of trends | Yes |
| Requires reframing | Yes |
| Systems \+ theory | Yes |
| Implementation feasible | Yes |
| Not just ML | Correct |
| Publishable abstraction | Yes |

This problem is **foundational**, not incremental.

It answers:

“What is identity, really, in distributed digital systems?”

That alone places it **above 90% of final-year projects**.

---