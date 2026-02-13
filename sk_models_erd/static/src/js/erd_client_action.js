/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useEffect, useRef, onWillStart } from "@odoo/owl";

class ERDClientAction extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.diagramDiv = useRef("diagramDiv");

        // Get the active model ID from the context passed by the action
        this.modelId = this.props.action.context.active_model_id;

        onWillStart(async () => {
            if (this.modelId) {
                this.erdData = await this.orm.call("ir.model", "get_erd_data", [this.modelId]);
            }
        });

        useEffect(() => {
            if (this.erdData && this.diagramDiv.el) {
                this.renderDiagram(this.diagramDiv.el, this.erdData);
            }
        });
    }

    renderDiagram(div, data) {
        // Check if GoJS is loaded
        if (typeof go === "undefined") {
            console.error("GoJS library not found.");
            div.innerHTML = "<div class='alert alert-danger'>GoJS library not found. Please download go.js and place it in sk_models_erd/static/lib/gojs/go.js</div>";
            return;
        }

        const $ = go.GraphObject.make;

        const myDiagram = $(go.Diagram, div, {
            "undoManager.isEnabled": true,
            layout: $(go.ForceDirectedLayout, {
                defaultSpringLength: 50,
                defaultElectricalCharge: 150,
                randomNumberGenerator: null // deterministic layout
            })
        });

        // Colors from the sample (Light Theme)
        const colors = {
            primary: '#f7f9fc',
            green: '#62bd8e',
            blue: '#3999bf',
            purple: '#7f36b0',
            red: '#c41000',
            stroke: '#e8f1ff',
            text: '#000000',
            link: '#888888'
        };

        // Item template for fields
        const fieldTemplate =
            $(go.Panel, "Horizontal",
                { margin: new go.Margin(1, 0) },
                $(go.Shape,
                    { width: 12, height: 12, strokeWidth: 0, margin: new go.Margin(0, 5, 0, 0), fill: colors.blue },
                    // Color code types: Many2one as purple, others blue
                    new go.Binding("fill", "type", t => (t === 'many2one' || t === 'one2many' || t === 'many22many') ? colors.purple : colors.blue)
                ),
                $(go.TextBlock,
                    { font: "13px sans-serif", stroke: "black" },
                    new go.Binding("text", "name"),
                    new go.Binding("font", "required", r => r ? "bold 13px sans-serif" : "13px sans-serif")
                ),
                $(go.TextBlock,
                    { font: "italic 11px sans-serif", margin: new go.Margin(2, 0, 0, 5), stroke: "#666" },
                    new go.Binding("text", "type")
                )
            );

        // Node Template
        myDiagram.nodeTemplate =
            $(go.Node, "Auto",
                {
                    selectionAdorned: true,
                    resizable: true,
                    layoutConditions: go.LayoutConditions.Standard & ~go.LayoutConditions.NodeSized,
                    fromSpot: go.Spot.LeftRightSides,
                    toSpot: go.Spot.LeftRightSides
                },
                $(go.Shape, "RoundedRectangle",
                    { stroke: colors.stroke, strokeWidth: 3, fill: colors.primary }
                ),
                $(go.Panel, "Table",
                    { margin: 8, stretch: go.GraphObject.Fill },
                    $(go.RowColumnDefinition, { row: 0, sizing: go.RowColumnDefinition.None }),

                    // Header
                    $(go.TextBlock,
                        {
                            row: 0, alignment: go.Spot.Center,
                            margin: new go.Margin(0, 10, 5, 10),
                            font: "bold 16px sans-serif",
                            stroke: colors.text
                        },
                        new go.Binding("text", "name")
                    ),

                    // Divider
                    $(go.Shape, "LineH",
                        {
                            row: 1, stretch: go.GraphObject.Horizontal,
                            stroke: colors.stroke, strokeWidth: 1, height: 1,
                            margin: new go.Margin(0, 0, 5, 0)
                        }
                    ),

                    // Fields List
                    $(go.Panel, "Vertical",
                        {
                            row: 2,
                            name: "FIELDS",
                            alignment: go.Spot.TopLeft,
                            defaultAlignment: go.Spot.Left,
                            itemTemplate: fieldTemplate
                        },
                        new go.Binding("itemArray", "fields", (fields) => {
                            // Limit to showing first 15 fields to avoid huge nodes
                            return fields ? fields.slice(0, 15) : [];
                        })
                    )
                )
            );

        // Link Template
        myDiagram.linkTemplate =
            $(go.Link,
                {
                    selectionAdorned: true,
                    routing: go.Link.AvoidsNodes,
                    corner: 5,
                    curve: go.Link.JumpOver
                },
                $(go.Shape, { stroke: colors.link, strokeWidth: 2 }),
                $(go.Shape, { toArrow: "Standard", stroke: colors.link, fill: colors.link }),
                $(go.TextBlock,
                    {
                        textAlign: "center",
                        font: "bold 12px sans-serif",
                        stroke: colors.link,
                        background: colors.primary,
                        segmentIndex: 0,
                        segmentOffset: new go.Point(NaN, NaN),
                        segmentOrientation: go.Link.OrientUpright
                    },
                    new go.Binding("text", "text")
                ),
                $(go.TextBlock,
                    {
                        textAlign: "center",
                        font: "bold 12px sans-serif",
                        stroke: colors.link,
                        background: colors.primary,
                        segmentIndex: -1,
                        segmentOffset: new go.Point(NaN, NaN),
                        segmentOrientation: go.Link.OrientUpright
                    },
                    new go.Binding("text", "toText")
                )
            );

        myDiagram.model = new go.GraphLinksModel(data.nodes, data.links);
        this.myDiagram = myDiagram;
    }

    downloadImage() {
        if (!this.myDiagram) return;

        // Create imageData
        const imageData = this.myDiagram.makeImageData({
            background: "white",
            scale: 1,
            type: "image/png"
        });

        // Trigger download
        const link = document.createElement('a');
        const filename = `ERD_Model_${this.modelId || 'Diagram'}.png`;
        link.href = imageData;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

ERDClientAction.template = "sk_models_erd.ERDClientAction";

registry.category("actions").add("sk_models_erd.erd_client_action", ERDClientAction);
