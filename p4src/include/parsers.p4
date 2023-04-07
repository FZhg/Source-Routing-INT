/*************************************************************************
*********************** P A R S E R  *******************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {

        transition parse_ethernet;

    }

    state parse_ethernet {

        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType){
            TYPE_IPV4: parse_ipv4;
            TYPE_SOURCE_ROUTING: parse_source_routing;
            default: accept;
        }
    }

    state parse_source_routing {
        packet.extract(hdr.source_routes.next);
        transition select(hdr.source_routes.last.last_header){
            1: parse_ipv4;
            default: parse_source_routing;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        //Check if ihl is bigger than 5. Packets without ip options set ihl to 5.
        verify(hdr.ipv4.ihl >= 5, error.IPHeaderWithoutOptions);
        transition select(hdr.ipv4.ihl) {
            5             : accept; // Not a INT probe
            default       : parse_ipv4_option;
        }
    }

        state parse_ipv4_option {
        packet.extract(hdr.ipv4_option);
        transition select(hdr.ipv4_option.option){

            IPV4_OPTION_INT:  parse_int;
            default: accept;

        }
     }

    state parse_int {
        packet.extract(hdr.int_count);
        meta.parser_metadata.num_headers_remaining = hdr.int_count.num_switches;
        transition select(meta.parser_metadata.num_headers_remaining){
            0: accept;
            default: parse_int_headers;
        }
    }

    state parse_int_headers {
        packet.extract(hdr.int_headers.next);
        meta.parser_metadata.num_headers_remaining = meta.parser_metadata.num_headers_remaining -1 ;
        transition select(meta.parser_metadata.num_headers_remaining){
            0: accept;
            default: parse_int_headers;
        }
    }


}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {

        //parsed headers have to be added again into the packet.
        packet.emit(hdr.ethernet);
        packet.emit(hdr.source_routes);
        packet.emit(hdr.ipv4);        
        packet.emit(hdr.ipv4_option);
        packet.emit(hdr.int_count);
        packet.emit(hdr.int_headers);

    }
}