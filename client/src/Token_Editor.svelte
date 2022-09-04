<script lang="ts">
import { Answer } from "./question_options";
import Question from './question_options'
import {clicked_id} from "./stores"
import { each } from "svelte/internal";


    export let tok_data : Map<string, string>
    export let trigger_update : boolean
    export let not_editable_keys : Array<string> = []
    export let dont_display_keys : Array<string> = []
    export let key_values_map : Map<string, Array<string>> = new Map<string, Array<string>>(
        [['Ellipsis', ['VPE', 'RNR', 'BadParse', 'Semantic']],
          ['Antecedent', ['Present', 'External', 'Exophoric']]]
    )

    let current_key = ''
    let value_buttons = []
    let add_mode = false
    let add_buttons = []
    export let is_editing_flag = false

    function reset_state() {
        current_key = ''
        value_buttons = []
        add_mode = false
        add_buttons = []
        is_editing_flag = false
    }

    let new_key_value = ''
    let current_id = tok_data ? tok_data.get('id') : ''

    function set_is_editing(e : Event, value : boolean, key:string) {
        is_editing_flag = value
        if(is_editing_flag) {
            key_click(key, true)
        } else { //blur
            let ef = e as FocusEvent
            console.log(ef.target)
            console.log(ef.currentTarget)
            console.log(ef.relatedTarget)
        }
    }

    function process_id_change(id : string) {
        console.log('Processing id change ' + id)
        console.log(is_editing_flag)
        if(!is_editing_flag) return
        tok_data.set(current_key, id)
        tok_data = tok_data
        is_editing_flag = false
    }

    function process_change(e : Event, key : string) {
        //console.log(e)
        let target = e.target as HTMLDivElement
        tok_data.set(key, target.textContent)
        tok_data = tok_data
        trigger_update = !trigger_update
    }

    function delete_key(key : string) {
        tok_data.delete(key)
        tok_data = tok_data
    }

    function add_key_click() {
        add_mode = true
        current_key = ''
        add_buttons = Array.from(key_values_map.keys()).filter(k => !tok_data.has(k))
    }

    function key_click(key : string, is_editing : boolean = false) {
        add_mode = false
        
        current_key = key
        is_editing_flag = is_editing
        let key_vals = key_values_map.get(key)
        if(key_vals == undefined) {
            value_buttons = []
        } else {
            value_buttons = key_vals
        }
        tok_data = tok_data
    }

    function on_value_button(value : string) {
        if(tok_data.has(current_key)) {
            tok_data.set(current_key, value)
            tok_data = tok_data
        }
    }

    function add_key_to_data(key : string) {
        if(tok_data.has(key)) {
            alert('Key ' + key + ' already exists!')
            return
        }
        tok_data.set(key, '')
        key_click(key)
        tok_data = tok_data
    }

    // reactive stuff
    clicked_id.subscribe(id => process_id_change(id))
    $: {
        tok_data;
        if(!tok_data || tok_data.get('id') != current_id)
            reset_state()
        current_id = tok_data ? tok_data.get('id') : ''
    }

</script>

{#if tok_data}
    <table class="token_editor">
        <tr><th class="token_editor">Key</th><th class="token_editor">Value</th><th class="token_editor">Fn</th></tr>
    {#each Array.from(tok_data.keys()) as key}
        {#if !dont_display_keys.includes(key)}
        <tr>
            <td class="token_editor"><div    on:click={()=>key_click(key)}
                        style={key==current_key ? "font-weight:bold;" : ""  }
                >
                {key}</div></td>
            <td class="token_editor"><div contenteditable={not_editable_keys.includes(key) ? "false" : "true"} 
                on:input={(e)=>process_change(e, key)}
                on:focus={(e)=> set_is_editing(e, true, key) }
                on:blur={(e)=> null  } 
            >{tok_data.get(key)}</div>
            </td>
            <td class="token_editor">
                {#if !not_editable_keys.includes(key)}
                    <button on:click={()=>delete_key(key)}>-</button>
                {/if}
            </td>
        </tr>
        {/if}
    {/each}
    <tr><td class="token_editor" colspan="3"><button on:click={add_key_click}>Add Key</button>
    </td></tr>
    </table>
    {#if value_buttons && current_key}
    <p>
        Change value <br/>
        {#each value_buttons as b}
            <button on:click={()=>on_value_button(b)}>{b}</button>
        {/each}
    </p>
    {/if}
    {#if add_mode}
    <p>
        Add key <br/>
        <input type="text" bind:value={new_key_value} size="10">
        <button on:click={()=>add_key_to_data(new_key_value)}>Add</button> <br/>
        {#each add_buttons as b}
        <button on:click={()=>add_key_to_data(b)}>{b}</button>
        {/each}
    </p>
    {/if}
    
{/if}

<style>
    .token_editor {
        border: 1px solid;
        border-collapse: collapse;
        background-color: ghostwhite;
    }

</style>