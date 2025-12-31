// Package models defines data structures for the ingestion service.
package models

// VerifiableCredential represents a W3C Verifiable Credential.
type VerifiableCredential struct {
	Context           []string               `json:"@context"`
	Type              []string               `json:"type"`
	ID                string                 `json:"id,omitempty"`
	Issuer            interface{}            `json:"issuer"` // Can be string or object
	IssuanceDate      string                 `json:"issuanceDate"`
	ExpirationDate    string                 `json:"expirationDate,omitempty"`
	CredentialSubject map[string]interface{} `json:"credentialSubject"`
	Proof             *Proof                 `json:"proof,omitempty"`
}

// Proof represents the cryptographic proof of a Verifiable Credential.
type Proof struct {
	Type               string `json:"type"`
	Created            string `json:"created"`
	VerificationMethod string `json:"verificationMethod"`
	ProofPurpose       string `json:"proofPurpose,omitempty"`
	ProofValue         string `json:"proofValue"`
}

// GetIssuerID extracts the issuer identifier from the issuer field.
func (vc *VerifiableCredential) GetIssuerID() string {
	switch v := vc.Issuer.(type) {
	case string:
		return v
	case map[string]interface{}:
		if id, ok := v["id"].(string); ok {
			return id
		}
	}
	return ""
}

// IsValid performs basic validation on the Verifiable Credential.
func (vc *VerifiableCredential) IsValid() bool {
	if len(vc.Context) == 0 {
		return false
	}
	if len(vc.Type) == 0 {
		return false
	}
	if vc.Issuer == nil {
		return false
	}
	if vc.IssuanceDate == "" {
		return false
	}
	if vc.CredentialSubject == nil {
		return false
	}
	return true
}

// OIDCClaims represents claims extracted from an OIDC ID Token.
type OIDCClaims struct {
	Issuer        string `json:"iss"`
	Subject       string `json:"sub"`
	Audience      string `json:"aud"`
	Expiration    int64  `json:"exp"`
	IssuedAt      int64  `json:"iat"`
	Email         string `json:"email,omitempty"`
	EmailVerified bool   `json:"email_verified,omitempty"`
	Name          string `json:"name,omitempty"`
	Picture       string `json:"picture,omitempty"`
	GivenName     string `json:"given_name,omitempty"`
	FamilyName    string `json:"family_name,omitempty"`
}
