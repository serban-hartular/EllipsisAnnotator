<script lang="ts">
	import TokenEditor from "./Token_Editor.svelte"
	import { onMount } from "svelte";
	import {clicked_id} from "./stores"
import { get } from "svelte/store";

	// let data = [{'form':'am', 'id':'0'}, {'form':'un', 'id':'1'}, {'form':'leu', 'id':'2'}]
	//let data_map = new Map(Object.entries(data))
	let token_list : Array<Map<string, string>> = [] //data.map(tok => new Map(Object.entries(tok)))
	// console.log(data_map_list)
	let selected = null

	let trigger_update = true

	let token_is_editing : boolean = false

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

	function to_html(token : Map<string, string>): string {
		let rep : string = token.get('form')
		if(token == selected) {
			rep = '<b><u>' + rep + '</u></b>'
		}
		if(selected && selected.has('TargetID') && selected.get('TargetID') == token.get('id')) {
			rep = '<b>' + rep + '</b>'
		}
		return rep
	}

	onMount(async () => {
		fetch("http://localhost:5000/tok-data")
		.then(response => response.json())
		.then(data => {
				console.log(data);
				token_list = data.map(tok => new Map(Object.entries(tok)))
		}).catch(error => {
			console.log(error);
			return [];
		});
	});

	let not_editable_keys = ['form', ]
	let dont_display_keys = ['str_after', 'sel', 'id']

	function save_json() {
		console.log(JSON.stringify(token_list.map(m => Object.fromEntries(m))))
	}

	function move_selected(delta : number) {
		let index = token_list.indexOf(selected)
		console.log(index)
		if(index < 0) return
		index = (index + delta) % token_list.length
		if(index < 0) index += token_list.length
		console.log(index)
		selected = token_list[index]
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

</script>

<main>
	<div class="text">
	<h1>Text:</h1>
	<p>
		{#each token_list as word}
			<span id={word.get('id')} on:click={() => span_click(word.get('id'))}>
				{@html to_html(word)} </span>
			{#if word.get('str_after') == '\n'}
			<br/>
			{/if}
		{/each}
	</p>
	</div>

	<div class="sidenav">
		<TokenEditor bind:tok_data={selected} bind:trigger_update={trigger_update}
				bind:not_editable_keys={not_editable_keys} 
				bind:dont_display_keys={dont_display_keys} 
				bind:is_editing_flag={token_is_editing}
		/>
		<hr/>
		<p>
			<button on:click={()=>move_selected(-1)}>Previous</button>
			<button on:click={()=>move_selected(1)}>Next</button>
		</p>
		<p>
			<button on:click={save_json}>Save JSON</button>
		</p>
	</div>
</main>

<style>
	main {
		text-align: left;
		padding: 1em;
		max-width: 240px;
		margin: 0 auto;
	}

	h1 {
		color: black;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
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
	.text {
		margin-left: 240px; /* Same as the width of the sidebar */
		padding: 0px 10px;
	}

</style>