export const getPortalUrl = (): string => {
  return "/portal";
};

export const getDigiLockerUrl = (targetSchemeId: string = "widow_pension"): string => {
  return `/auth/digilocker/login?target_scheme_id=${encodeURIComponent(targetSchemeId)}`;
};

export const getApiDocsUrl = (): string => {
  return "/docs";
};

