import { CapacitorConfig } from "@capacitor/cli"

const config: CapacitorConfig = {
	appId: "io.frappe.frappe_npo",
	appName: "Changemakers",
	webDir: "../frappe_npo/public/frontend",
	bundledWebRuntime: false,
	plugins: {
		CapacitorHttp: {
			enabled: true,
		},
	},
}

export default config
