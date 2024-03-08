from flask import Flask, render_template, request, flash, url_for, redirect
from server.modules import odl_api
import json
import traceback

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

odl_api.get_topo(forced=True)


@app.route("/")
@app.route("/topo")
def topology():
    try:
        list_switch, list_host = odl_api.get_topo()
        return render_template('topology.html', list_switch=list_switch, list_host=list_host)
    except Exception as e:
        traceback.print_exc()
        flash(str(e), 'danger')
        return render_template('topology.html')


@app.route("/config")
def config():
    try:
        list_switch, list_host = odl_api.get_topo()
        links_graph = {}
        for switch in list_switch:
            links_graph[switch.node_name] = list(
                map(lambda x: x.dst_name, switch.node_link))
        for host in list_host:
            links_graph[host.node_name] = list(
                map(lambda x: x.dst_name, host.node_link))
        return render_template('config.html', list_switch=list_switch, list_host=list_host, links_graph=json.dumps(links_graph))
    except Exception as e:
        traceback.print_exc()
        flash(str(e), 'danger')
        return render_template('config.html')


@app.route("/flows")
def flows():
    try:
        switch = request.args.get('switch')
        list_switch, list_host = odl_api.get_topo()
        if not switch:
            return render_template('flows.html', list_switch=list_switch)
        flows = odl_api.get_flow(switch)
        for flow in flows:
            actions = list(
                map(lambda x: f"{x['action']}({x.get('rule', '')})", flow['actions']))
            flow['actions'] = actions
        return render_template('flows.html', list_switch=list_switch, flows=flows, switch=switch)
    except Exception as e:
        traceback.print_exc()
        flash(str(e), 'danger')
        return redirect(url_for('flows'))


@app.route("/flows/add", methods=["POST"])
def add_flow():
    try:
        switch_name = request.form["switch"]
        inport = request.form["inport"]
        outport = request.form["outport"]
        src = request.form["src"]
        dst = request.form["dst"]
        odl_api.add_flow(switch_name, 'icmp', inport, outport, src, dst)
        odl_api.add_flow(switch_name, 'arp', inport, outport, src, dst)

        flash("Added flow successfully.", 'success')
    except Exception as e:
        traceback.print_exc()
        flash(str(e), 'danger')
    return redirect(url_for('config'))


@app.route("/flows/delete", methods=["POST"])
def delete_flow():
    import os
    os.system("clear")
    try:
        switch_name = request.form["switch"]
        if switch_name == 'all':
            odl_api.delete_all_flow()
            flash("Deleted flows on all switches successfully.", 'success')
        else:
            odl_api.delete_flow(switch_name)
            flash(
                f"Deleted flows on switch {switch_name} successfully.", 'success')
    except Exception as e:
        traceback.print_exc()
        flash(str(e), 'danger')
    return redirect(url_for('config'))


@app.route("/route/dijkstra", methods=["POST"])
def route_dijkstra():
    try:
        src = request.form["src"]
        dst = request.form["dst"]
        # mode = request.form["mode"]
        # is_private = mode == 'private'
        path = odl_api.route_dijkstra([src, dst])
        newpath = []
        print(src, dst)
        for item in path:
            if 'host' in item:
                node_name = 'h' + str(int(item.split(":")[-1], 16))
                newpath.append(node_name)
            if 'openflow' in item:
                node_name = 's' + item.split(":")[-1]
                newpath.append(node_name)
        path_str = "→".join(newpath)
        flash(
            f"Find route using Dijkstra from {src} to {dst} successfully: {path_str}.", 'success')
    except Exception as e:
        traceback.print_exc()
        flash(str(e), 'danger')
    return redirect(url_for('config'))


@app.route("/route/custom", methods=["POST"])
def route_custom():
    try:
        path_str = request.form["path"]
        path = path_str.split(",")

        # mode = request.form["mode"]
        # is_private = mode == 'private'
        odl_api.route_custom(path)
        flash(f"Find custom route {path_str} successfully.", 'success')
    except Exception as e:
        traceback.print_exc()
        flash(str(e), 'danger')
    return redirect(url_for('config'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
    print(123)

# dpctl dump-flows -O OpenFlow13
