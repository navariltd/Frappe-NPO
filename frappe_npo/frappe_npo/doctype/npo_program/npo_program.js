// Copyright (c) 2026, Navari Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("NPO Program", {
	refresh(frm) {
		let wrapper = frm.fields_dict["program_summary"].$wrapper;
		wrapper.empty();

		if (!frm.doc.__islocal) {
			fetchProjects(frm);
		}
	},

	refresh: (frm) => {
		fetchProjects(frm);
	},
});

function fetchProjects(frm) {
	frappe.call({
		method: "fetch_projects",
		doc: frm.doc,
		callback: (res) => {
			let container = createContainer(frm);
			renderProjects(res.message, container);
		},
		error: () => {
			frappe.msgprint(_("Error fetching projects"));
		},
	});
}

function renderProjects(projects, container) {
	if (!projects || !projects.length) {
		$(container).html(
			'<p class="text-muted" style="padding: 10px;">No projects found for this program.</p>',
		);
		return;
	}

	let rows = mapProjectsToDataTable(projects);

	new frappe.DataTable(container, {
		columns: [
			{
				name: "Project",
				width: 2,
				format: cellFormatter("project"),
			},
			{
				name: "Title",
				width: 2,
			},
			{ name: "Task", width: 3, format: cellFormatter("task") },
			{ name: "Task Name", width: 3 },
		],
		data: rows,
		layout: "fluid",
		cellHeight: 35,
		treeView: true,
		serialNoColumn: false,
		inlineFilters: true,
	});
}

function mapProjectsToDataTable(projects) {
	let rows = [];
	projects.forEach((project) => {
		rows.push({
			Project: project.project,
			Title: project.project_name,
			Task: "",
			"Task Name": "",
			indent: 0,
		});

		if (project.tasks && project.tasks.length) {
			project.tasks.forEach((task) => {
				rows.push({
					Project: "",
					Task: task.task,
					"Task Name": task.task_name,
					indent: 1,
				});
			});
		}
	});

	return rows;
}

function cellFormatter(doctype) {
	return (value) => {
		if (!value) return "";
		return `<a href="/app/${doctype}/${value}" target="_blank">${value}</a>`;
	};
}
function createContainer(frm) {
	let wrapper = frm.fields_dict["program_summary"].$wrapper;
	wrapper.empty();
	let container = $("<div>").appendTo(wrapper)[0];

	return container;
}
