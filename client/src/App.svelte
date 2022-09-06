<script lang="ts">
	import TokenEditor from "./Token_Editor.svelte"
	import { onMount } from "svelte";
	import {clicked_id} from "./stores"

	let token_list : Array<Map<string, string>> = [] //data.map(tok => new Map(Object.entries(tok)))
	let selected = null
	let trigger_update = true
	let token_is_editing : boolean = false
	let token_filter_expr = "token.has('Ellipsis')"
	let doc_name = ''
	let current_file_name = ''
	let save_changes_flag = true

	let doc_id_str = 'newdoc id'
	let token_key_str = 'tokens'


	$: {
		trigger_update;
		console.log('trigger update changed')
		token_list = token_list
	}	

	function span_click(id : string) {
		console.log('clicked ' + id)
		if(!token_is_editing)
			for(let word of token_list) {
				if(word.get('id') == id) {
					selected = word
				}
			}
		clicked_id.update(n => id)
		token_list = token_list
	}

	function get_word_class(word : Map<string, string>) : string {
		if(word == selected) {
			return 'selected' 
		}
		if(selected && selected.has('TargetID') && selected.get('TargetID') == word.get('id')) {
			return 'target'
		}
		return 'normal'
	}

	function server_data_to_token_list(data) {
		doc_name = data[doc_id_str]
		let tokens = data[token_key_str]
		token_list = tokens.map(tok => new Map(Object.entries(tok)))
		selected = null
		window.scrollTo(0, 0)
	}

	onMount(async () => {
		console.log('get-init-doc')
		fetch("http://localhost:5000/get-init-doc")
		.then(response => response.json())
		.then(data => {
				//console.log(data);
				server_data_to_token_list(data)
		}).catch(error => {
			console.log(error);
			return [];
		});
	});


	function fetch_doc_delta(delta : number) {
		if(delta != 0 && save_changes_flag) {
			update_doc()
		}
		fetch("http://localhost:5000/get-doc-relative", {
			method: 'POST', // *GET, POST, PUT, DELETE, etc.
			// mode: 'cors', // no-cors, *cors, same-origin
			// cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
			// credentials: 'same-origin', // include, *same-origin, omit
			headers: {
			'Content-Type': 'application/json'
			},
			body: JSON.stringify({'delta':delta})
		})
		.then(response => response.json())
		.then(data => server_data_to_token_list(data))
	}

	function update_doc() {
		fetch("http://localhost:5000/update-doc", {
			method: 'POST', 
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({[doc_id_str]:doc_name,
						[token_key_str]:token_list.map(m => Object.fromEntries(m))})
		})
		.then(response => response.json())
		.then(data => {
				console.log(data);
		})
	}

	let not_editable_keys = ['form', 'id']
	let dont_display_keys = ['str_after']

	function save_json() {
		console.log(JSON.stringify(token_list.map(m => Object.fromEntries(m))))
	}

	function move_selected(delta : number) {
		let index = selected ? token_list.indexOf(selected) : 0
		//let init_index = index
		if(index < 0) return
		let initial_index = index
		delta = Math.sign(delta)
		let token = token_list[index]
		while(true) {
			index = (index + delta) % token_list.length
			if(index < 0) index += token_list.length
			token = token_list[index]
			if(index == initial_index) {
				alert('No other token found according to criteria')
				break
			}
			if(!token_filter_expr)
				break
			let token_eval = false
			try {
				token_eval = eval(token_filter_expr)
			} catch {
				alert('Invalid expression ' + token_filter_expr + 
				'\n' + '(name of key-value variable is "token"')
				token = token_list[initial_index]
				token_eval = true
			}
			if(token_eval) {
				break
			}
		}
		selected = token
		trigger_update = !trigger_update
		if(!isInViewport(selected.get('id'))) {
			document.getElementById(selected.get('id')).scrollIntoView()
		}
	}

	function isInViewport(id : string) : boolean {
		let el = document.getElementById(id)
		const rect = el.getBoundingClientRect();
		return (
			rect.top >= 0 &&
			rect.left >= 0 &&
			rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
			rect.right <= (window.innerWidth || document.documentElement.clientWidth)

		);
	}

	let file_list : Array<string> = []

	function commit_to_server() {
		fetch("http://localhost:5000/save-to-server")
		.then(response => response.json())
		.then(data => {
			console.log(data);
		})
	}

	function get_file_list() {
		fetch("http://localhost:5000/get-file-list")
		.then(response => response.json())
		.then(data => {
			console.log(data);
			file_list = data
			// let list_select = document.getElementById('file_list') as HTMLSelectElement
			// list_select.click()
		})
	}
	let file_name = ''

	function load_file(name : string) {
		//tell server to load filename
		let load_ok = false
		fetch("http://localhost:5000/load-file", {
				method: 'POST', 
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({'filename':name})
		})
		.then(response => response.json())
		.then(data => {
			console.log(data);
			if(data['response'] == 'ok') {
				current_file_name = name
				load_ok = true
			} else {
				current_file_name = data['error']
			}
		})
		if(!load_ok) return
		//load first doc in file	
		fetch("http://localhost:5000/get-init-doc")
		.then(response => response.json())
		.then(data => {
				//console.log(data);
				server_data_to_token_list(data)
		}).catch(error => {
			console.log(error);
			return [];
		});

	}

</script>

<main>
	<div class="text">
	<h2>File: {current_file_name}</h2>
	<h2>Text: {doc_name}</h2>
	<p>
		{#each token_list as word}
			<span id={word.get('id')} class={get_word_class(word)} on:click={() => span_click(word.get('id'))}>
				<!-- {@html to_html(word)} </span> -->
				{word.get('form')} </span>
			{#if word.get('str_after') == '\n'}
			<br/>
			{/if}
		{/each}
	</p>
	</div>

	<div class="sidenav" on:click|self={()=>console.log('sidenav click')}>
		<div class="token_editor">
			<TokenEditor bind:tok_data={selected} bind:trigger_update={trigger_update}
					bind:not_editable_keys={not_editable_keys} 
					bind:dont_display_keys={dont_display_keys} 
					bind:is_editing_flag={token_is_editing}
			/>
		</div>
		<hr/>
		<p>
			<button on:click={()=>move_selected(-1)}>Previous Token</button>
			<button on:click={()=>move_selected(1)}>Next Token</button> <br/>
				Next/Previous token criteria
				<input type="text" bind:value={token_filter_expr} />
	
		</p>
		<p>
			<button on:click={()=>fetch_doc_delta(-1)}>Previous Doc</button>
			<button on:click={()=>fetch_doc_delta(+1)}>Next Doc</button><br/>
			Keep Changes <input type="checkbox" bind:checked={save_changes_flag} />
		</p><p>
			<button on:click={()=>fetch_doc_delta(0)}>Reload Doc</button>
		</p>
		<p><button on:click={commit_to_server}>Commit Changes to Server</button></p>
		<p>
			<button on:click={get_file_list}>Load File</button>
			<select id="file_list" bind:value={file_name} on:change={()=>load_file(file_name)}>
				{#each file_list as name}
				<option value={name}>{name}</option>
				{/each}
			</select>
		</p>
	</div>
</main>

<style>
	main {
		text-align: left;
		padding: 1em;
		max-width: 240px;
		margin: 0 auto;
		font-size: 1em;
		/* font-family: Arial, Helvetica, sans-serif;
		font-size: 16px;		 */
	}

	.sidenav {
		font-size: 0.8em;
	}

	/* h1 {
		color: black;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
	} */

	h2 {
		color: black;
		font-size: 2em;
		/* font-weight: 100; */
	}


	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
	.sidenav {
		height: 100%; /* Full-height: remove this if you want "auto" height */
		width: 240px; /* Set the width of the sidebar */
		position: fixed; /* Fixed Sidebar (stay in place on scroll) */
		z-index: 1; /* Stay on top */
		top: 0; /* Stay at the top */
		left: 0;
		background-color: #fbfbfb;
		overflow-x: hidden; /* Disable horizontal scroll */
		padding-top: 20px;
		padding-left: 20px;
	}
	div.token_editor {
		min-height: 15em;
	}
	.text {
		margin-left: 240px; /* Same as the width of the sidebar */
		padding: 0px 10px;
	}
	span.selected {
		font-weight: bold;
		text-decoration: underline;
		color: red;
		font-size: larger;
	}
	span.target {
		font-weight: bold;
		color: black;
	}
	span.normal {
		color: black;
	}

</style>