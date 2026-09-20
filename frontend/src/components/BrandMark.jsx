import logoPrincipal from "../assets/brand/logo-principal.png";
import logoSecundary from "../assets/brand/logo-secondary.png";

function BrandMark({ compact = false }) {
    return (
        <div
            className={compact ? "ara-brand compact" : "ara-brand"}
            aria-label="A.R.A."
        >
            <img
                src={compact ? logoSecundary : logoPrincipal}
                alt="A.R.A."
                className={
                    compact
                        ? "ara-brand-logo compact-logo"
                        : "ara-brand-logo"
                }
            />
        </div>
    );
}

export default BrandMark;