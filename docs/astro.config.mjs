import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";
import { unified } from "@astrojs/markdown-remark";
import apiSidebar from "./src/generated/api-sidebar.json";

export default defineConfig({
  outDir: "./_build",
  site: "https://natlabrockies.github.io",
  base: "/plexosdb/",
  markdown: { processor: unified() },
  integrations: [
    starlight({
      title: "plexosdb",
      description: "Python tools for reading, building, and writing PLEXOS models.",
      social: [
        {
          icon: "github",
          label: "GitHub",
          href: "https://github.com/NatLabRockies/plexosdb",
        },
      ],
      editLink: {
        baseUrl: "https://github.com/NatLabRockies/plexosdb/edit/main/docs/src/content/docs/",
      },
      customCss: ["./src/styles/brand.css"],
      sidebar: [
        {
          label: "Getting started",
          items: [{ label: "Installation", link: "/getting-started/installation/" }],
        },
        {
          label: "Tutorial",
          items: [{ label: "Build a PLEXOS database", link: "/tutorials/tutorial/" }],
        },
        {
          label: "How-to guides",
          items: [
            { label: "Overview", link: "/how-to/" },
            { label: "Create a database", link: "/how-to/create_db/" },
            { label: "Add objects", link: "/how-to/add_objects/" },
            { label: "Add properties", link: "/how-to/add_properties/" },
            { label: "Add attributes", link: "/how-to/add_attributes/" },
            { label: "Add reports", link: "/how-to/add_reports/" },
            { label: "Delete objects", link: "/how-to/delete_objects/" },
            { label: "Query a database", link: "/how-to/query_database/" },
            { label: "Work with scenarios", link: "/how-to/work_with_scenarios/" },
            { label: "Import and export", link: "/how-to/import_export/" },
            { label: "Validate a database", link: "/how-to/validate_database/" },
            { label: "Manage relationships", link: "/how-to/manage_relationships/" },
            { label: "Copy objects", link: "/how-to/copy_objects/" },
            { label: "Bulk operations", link: "/how-to/bulk_operations/" },
            { label: "Remove non-ASCII text", link: "/how-to/remove_non_ascii/" },
            { label: "Inspect a solution", link: "/how-to/inspect_solution/" },
            { label: "Read a solution", link: "/how-to/read_solution/" },
            { label: "MCP server", link: "/how-to/mcp_server/" },
          ],
        },
        {
          label: "Reference",
          items: [
            {
              label: "Python API",
              collapsed: true,
              items: [{ label: "Overview", link: "/reference/python-api/" }, ...apiSidebar.exports],
            },
            {
              label: "Module guides",
              collapsed: true,
              items: apiSidebar.modules,
            },
            {
              label: "PLEXOS attribute tables",
              collapsed: true,
              items: [
                { label: "Model", link: "/reference/api/model_attributes/" },
                { label: "Production", link: "/reference/api/production_attributes/" },
                { label: "Performance", link: "/reference/api/performance_attributes/" },
                { label: "Transmission", link: "/reference/api/transmission_attributes/" },
                { label: "PASA", link: "/reference/api/pasa_attributes/" },
                { label: "Diagnostics", link: "/reference/api/diagnostic_attributes/" },
                { label: "Horizon", link: "/reference/api/horizon_attributes/" },
                { label: "MT schedule", link: "/reference/api/mt_schedule_attributes/" },
                { label: "ST schedule", link: "/reference/api/st_schedule_attributes/" },
                { label: "LT plan", link: "/reference/api/lt_plan_attributes/" },
              ],
            },
          ],
        },
        { label: "Changelog", link: "/changelog/" },
      ],
    }),
  ],
});
