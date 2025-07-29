def SmartsCalc( e ) :
    equation = e
    def tsttool( l ) :
        from random import randint
        l = randint( 2 , l )
        s = "%+-*/"
        sol = "" + str( randint( 1 , 9 ) )
        for i in range( l -1 ) :
            r = randint( 0 , len( s ) -1 )
            sol += s[r] + str( randint( 1 , 9 ) )
        return sol

    #TO DEL 'UP' hear
    """
    1=read the equation
    2=slice if to symboles and numbers
    3=do the first calc */%
    4=do the last calc +-
    5=return the result
    """
    #data
    NL = []
    SL = []
    #read the solution
    #    if not ( str(e).isalpha() ):
    #       e=tst(e)
    #slice
    def GSI( eq ) :
        for i in range( len( eq ) ) :
            if eq[ i ] in "+-*/%" :
                return i
        return False
    def GFN( eq ) :
            return eq[ : GSI( eq ) ]
    def DFN( eq ) :
            return eq[ GSI( eq ) : ]
    def GS( eq ) :
            return eq[ GSI( eq ) ]
    def DS( eq ) :
            return eq[ GSI( eq ) +1 : ]
    def SSexistingTST( eq ) :#special symboles existing tst
            ss = 0
            for i in range( len( eq ) ) :
                if eq[ i ] in "*/%" :
                    ss += 1
            if ss > 0 :
                return True
            else :
                return False
    def NSonlyTST( eq ) :#NORMAL SYMBOLES ONLY - TEST
            ns = 0
            for i in range( len( eq ) ) :
                if eq[ i ] in "+-" :
                    ns += 1
            if ns > 0 :
                return True
            else :
                return False
    #1st step 'get the first and delit then get the lasts and delet'
    NL.append( GFN( e ) )
    e = DFN( e )
    while e :
            SL.append( GS( e ) )
            e = DS( e )
            if GSI( e ) is False :
                NL.append( e )
                e = DFN( e )
                break
            NL.append( GFN( e ) )
            e = DFN( e )
    #print(f"THE SYMBOLES EXIST NOW:{SL}\nTHE NUMBERS EXIST NOW:{NL}")
    #TOURNUMBER=1
    while len( SL ) > 0 and SSexistingTST(SL):
        if SL[ GSI( SL ) ] == "*" :
            NL[ GSI( SL ) ] = float( NL[ GSI( SL ) ] ) * float( NL[ GSI( SL ) +1 ] )
            NL.remove( NL[ GSI( SL ) +1 ] )
            SL.remove( SL[ GSI( SL ) ] )
        elif SL[ GSI( SL ) ] == "/" :
            NL[ GSI( SL) ] = float( NL[ GSI( SL ) ] ) / float( NL[ GSI( SL ) +1 ] )
            NL.remove( NL[ GSI( SL ) +1 ] )
            SL.remove( SL[ GSI( SL ) ] )
        elif SL[ GSI( SL ) ] == "%" :
            NL[ GSI( SL ) ] = float( NL[ GSI( SL ) ] ) % float( NL[ GSI( SL ) +1 ] )
            NL.remove( NL[ GSI( SL ) +1 ] )
            SL.remove( SL[ GSI( SL ) ] )
    #    print(f"{"\n"*10}TOUR NUMBER:{TOURNUMBER}\nTHE SYMBOLES EXIST NOW:{SL}\nTHE NUMBERS EXIST NOW:{NL}")
    #    print(f"LENGTH OF SL:{len( SL )}\nEXISTING OF SPECIAL SYMBOLES:{SSexistingTST(SL)}")
    #    TOURNUMBER+=1
    #print(f"THE SYMBOLES EXIST NOW:{SL}\nTHE NUMBERS EXIST NOW:{NL}")
    #TOURNUMBER=1
    while len( SL ) > 0 and NSonlyTST( SL ) :
        if SL[ GSI( SL ) ] == "+" :
            NL[ GSI( SL ) ] = float( NL[ GSI( SL ) ] ) + float( NL[ GSI( SL ) +1 ] )
            NL.remove( NL[ GSI( SL ) +1 ] )
            SL.remove( SL[ GSI( SL ) ] )
        elif SL[ GSI ( SL ) ] == "-" :
            NL[ GSI ( SL ) ] = float( NL [ GSI(SL) ] ) - float( NL[ GSI(SL) + 1 ] )
            NL.remove( NL[ GSI( SL ) +1 ] )
            SL.remove( SL[ GSI( SL ) ] )
    #    print(f"{"\n"*10}TOUR NUMBER:{TOURNUMBER}\nTHE SYMBOLES EXIST NOW:{SL}\nTHE NUMBERS EXIST NOW:{NL}")
    #    print(f"LENGTH OF SL:{len( SL )}\nEXISTING OF SPECIAL SYMBOLES:{SSexistingTST(SL)}")
    #    TOURNUMBER+=1
    RESULT = NL[ 0 ]
    #print(f'{equation}={RESULT}')
    return RESULT
#print(SmartsCalc("4/3*2"))
#print(4/3*2)