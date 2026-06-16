class ThresholdEngine:

    def __init__(self, thresholds):
        self.thresholds = thresholds

    def check(self, latest):

        alerts = []

        for kpi, threshold in self.thresholds.items():

            if kpi not in latest:
                continue

            value = latest[kpi]

            # Special case: Shipping days (lower is better)
            if kpi == "avg_shipping_days":

                if value > threshold:
                    alerts.append(
                        f"⚠ ALERT: {kpi.upper()} exceeded threshold ({value:.2f} > {threshold})"
                    )

            # Normal KPIs (higher is better)
            else:

                if value < threshold:
                    alerts.append(
                        f"⚠ ALERT: {kpi.upper()} dropped below threshold ({value:.2f} < {threshold})"
                    )

        return alerts