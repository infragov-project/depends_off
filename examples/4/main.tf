/*
 * This example demonstrates redundant `depends_on` usage between modules.
 */

// main.tf

module "network" {
  source = "./modules/network"
}

module "app" {
  source     = "./modules/app"
  subnet_id = module.network.subnet_id
  depends_on = [module.network.subnet_id]
}
