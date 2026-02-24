import { FullConfig, request } from "@playwright/test";

async function globalSetup(config: FullConfig) {
  const requestContext = await request.newContext();

  await requestContext.post(
    "http://frappe_npo.localhost:8000/api/method/login",
    {
      data: {
        usr: "Administrator",
        pwd: "admin",
      },
    },
  );
  // Save signed-in state to 'storageState.json'.
  // await requestContext.storageState({ path: "storageState.json" });
  await requestContext.dispose();
}

export default globalSetup;
