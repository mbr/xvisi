from xvisi import all_sites

if __name__ == '__main__':
    print list(all_sites[0].search('simpsons'))
    print list(all_sites[0].get_front())
