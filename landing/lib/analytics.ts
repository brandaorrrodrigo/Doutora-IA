// Analytics tracking functions for Google Tag Manager / GA4

export const trackCTAClick = (ctaName: string) => {
  if (typeof window !== 'undefined' && (window as any).dataLayer) {
    (window as any).dataLayer.push({
      event: 'cta_click',
      cta_name: ctaName,
    });
  }
};

export const trackLeadSubmit = (leadData: any) => {
  if (typeof window !== 'undefined' && (window as any).dataLayer) {
    (window as any).dataLayer.push({
      event: 'lead_submit',
      ...leadData,
    });
  }
};

export const trackPlanSelect = (planName: string, price: string) => {
  if (typeof window !== 'undefined' && (window as any).dataLayer) {
    (window as any).dataLayer.push({
      event: 'plan_select',
      plan_name: planName,
      plan_price: price,
    });
  }
};

export const trackROICalculation = (result: number) => {
  if (typeof window !== 'undefined' && (window as any).dataLayer) {
    (window as any).dataLayer.push({
      event: 'roi_calculation',
      roi_result: result,
    });
  }
};
