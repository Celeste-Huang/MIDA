module obsdrivers
 ! meteorological drivers
 double precision :: maxt,mint,rad,day,ca,lat,doy,vpd
 double precision, parameter ::  psid=-2.0d0  !water potential gradient
 double precision, parameter ::  rtot=1.0d0   !hydraulic resistance
 integer ncycles
 logical decid
end module obsdrivers

module parameters
 ! parameters in the modified DALEC model
 double precision gdd_min, gdd_max, laimax, tsmin, leaffall
 double precision nue, rg_frac, br_mr, q10_mr
 double precision astem, tleaf, troot, tstem
 double precision q10_hr, br_lit, br_som, dr, lma, leafcn
 double precision leafc_init, stemc_init, rootc_init
 double precision litc_init, somc_init
end module parameters

program DALEC_deciduous
  use obsdrivers
  use parameters
  implicit none
  double precision :: driver(7,365*2000), model(8,365*2000)
  ! model states
  double precision :: LAI, Trate, litfall(2), veg_pools(4)
  double precision :: soil_pools(2), GDD, RG, RM, NPP, NPP2
  double precision :: CF_DELTA, GPP, HR, LAI_last


  integer :: i, n
  integer :: nday
  logical :: dowrite
  character(3) site

  ! set parameters
  open(unit=12, file='./paramValue.txt')
  read(12,*) gdd_min
  read(12,*) gdd_max
  read(12,*) laimax
  read(12,*) tsmin
  read(12,*) leaffall
  read(12,*) nue
  read(12,*) rg_frac
  read(12,*) br_mr
  read(12,*) q10_mr
  read(12,*) astem
!read(12,*) tleaf !modified by Xin 
  read(12,*) troot
  read(12,*) tstem
  read(12,*) q10_hr
  read(12,*) br_lit
  read(12,*) br_som
  read(12,*) dr
  read(12,*) lma
  !read(12,*) leafcn !modified by Xin
  read(12,*) stemc_init
  read(12,*) rootc_init
  read(12,*) litc_init
  read(12,*) somc_init
  !print*, gdd_min, gdd_max, laimax

  gdd_min  = 100.d0          ! Growing degree day threshold for leafout
  !gdd_max  = 200.d0          ! Growing degree day threshold for maximum LAI
  !laimax   = 4.0d0           ! Seasonal maximum leaf area index
  !tsmin    = 5.0d0           ! Temperature for leaffall
  !1eaffall = 0.1d0           ! rate of leaffall
  !nue      = 7.0d0           ! Nitrogen use efficiency
  !rg_frac  = 0.2d0           ! growth respiration fraction
  !br_mr    = 0.0001d0        ! Base rate for maintenance respiration
  !q10_mr   = 2.0d0           ! Maintenance respiration T-sensitivity
  !astem    = 0.7d0           ! Allocation to plant stem pool
  !tleaf    = 0.01d0          ! leaf turnover time (days)
  !troot    = 1.0/5.0/365.0   ! root turnover time
  !tstem    = 1.0/50.0/365.0  ! stem turnover time
  !q10_hr   = 2.0d0           ! temperature sensitivity for heterotrophic respiration
  !br_lit   = 1.0/2.0/365.0   ! base turnover for litter
  !br_som   = 1.0/30.0/365.0  ! base turnover for soil organic matter
  !dr       = 0.001d0         ! decomposition rate
  !lma      = 80.0d0          ! specific leaf area
  !leafcn   = 25.0d0          ! leaf C:N ratio
  !print *, gdd_min, gdd_max, laimax,tsmin,leaffall,nue,rg_frac,br_mr,q10_mr,astem,troot,tstem,q10_hr,br_lit,br_som,dr,lma,&
  !stemc_init,rootc_init,litc_init,somc_init
  tleaf=0.01
  leafcn=25.0
  ! input
  lat  = 45.0d0               ! latitude
  lat  = lat*3.14159265358979d0/180.d0 ! convert latitude to radians
  nday=5844                   ! number of days in driver dataset
  ncycles=1                 ! number of cycles over driver dataset (for spinup)

  open(11, file='./US-Ha1_drivers.csv')
  do i=1,nday
    read(11,*) driver(1:5,i)
  end do
  close(11)
  open(26, file='./simuNEE.txt')
  
  veg_pools(1) = leafc_init
  veg_pools(2) = stemc_init
  veg_pools(3) = rootc_init
  soil_pools(1) = litc_init
  soil_pools(2) = somc_init
  
  do n=1,ncycles
    do i=1,nday
      ! Read in drivers for day
      doy   = MOD(i,365)+1   ! driver(1,i)  ! day of year
      mint  = driver(2,i)-273.15d0    ! minimum temperature (C)
      maxt  = driver(3,i)-273.15d0    ! maximum temperature (C)
      rad   = driver(4,i)    ! global radiation (MJ m-2 d-1)
      vpd   = 1.0d0 !driver(5,i) ! vapor pressure deficit
      ca    = driver(5,i)    ! carbon dioxide concentration
      decid = .true.         ! deciduous phenology

      if (doy .eq. 1) GDD=0.0d0  !reset GDD on DOY 1
      GDD=GDD+max(0.5d0*(maxt+mint)-10.0d0,0.0d0) ! growing degree day heat sum 

      ! calculate deciduous phenology
      if (decid) then 
        LAI_last = LAI
        call phenology(GDD, LAI)
        CF_DELTA = (LAI-LAI_LAST)*lma  ! change in leaf mass
      else
        LAI = laimax
        CF_DELTA = tleaf*VEG_POOLS(1)
      end if
   
      ! get gross primary productivity
      if (LAI .gt. 0) then 
        call Phot(LAI, GPP)
      else
        GPP=0d0
      end if
      ! get autotrophic respiration
      call Ra(VEG_POOLS, CF_DELTA, GPP, RG, RM)
      NPP  = GPP-RG-RM
      NPP2 = NPP
      if (CF_DELTA .gt. 0) NPP2 = NPP-CF_DELTA

      ! allocate carbon 
      call allocate(CF_DELTA, VEG_POOLS, NPP2)

      ! litter fall
      call litterfall(CF_DELTA, VEG_POOLS, SOIL_POOLS, LITFALL)

      ! decomposition
      call decomp(SOIL_POOLS, HR)

      !write(*,'(I5,10(f10.3,1x))'), i, HR-NPP, GPP, HR, LAI, VEG_POOLS(1:3), SOIL_POOLS	

      model(1,i) = (HR-NPP) ! NEE
      if(i .eq. 1)then
          if(model(1,1) .gt. 67) then
          print *,HR
          print *,NPP
          end if
      end if
      model(2,i) = GPP      ! GPP
      model(3,i) = HR       ! LAI
      ! for predictions
      model(4,i) = LAI
      model(5,i) = VEG_POOLS(1)+VEG_POOLS(2)+VEG_POOLS(3)
      model(6,i) = SOIL_POOLS(1)+SOIL_POOLS(2)
      !write(*,'(I5,8(f10.3,1x))'), i, model(:,i)
      !if (dowrite) then 
        !write(26,'(I5,1(E20.12,1x))') i, model(1:1,i)
        write(26, '(E20.12)') model(1,i)
        !write(1000, '(E20.12)') HR
        !write(1001, '(E20.12)') NPP
      !end if 
    end do
  end do 

  !print *,model(1,1)
  close(26)

end program DALEC_deciduous


!------------------------------------------------------------------
subroutine Ra(VEG_POOLS, CF_DELTA, GPP, RG, RM)
  ! parameters rg_frac, br_mr, q10_mr
  use obsdrivers
  use parameters
  implicit none
  double precision :: VEG_POOLS(3), GPP, NPP, CF_DELTA
  double precision :: Trate, Rg, Rm

  ! calculate Q10 temperature factor for maintenace respiration
  Trate  = q10_mr**((0.5d0*(maxt+mint)-10.d0)/10.d0) 
  ! calculate maintenance respiration (leaf and root only)
  Rm = (VEG_POOLS(1)+VEG_POOLS(3))*br_mr*Trate

  ! calculate growth respiration 
  Rg=0.0d0
  if (GPP-Rm .gt. 0.0d0) then 
    Rg = rg_frac*(GPP-Rm)
  end if

  ! growth respiration to force growing leaves if GPP exceeded
  if ( (CF_DELTA .gt. GPP-Rm) .and. (CF_DELTA .gt. 0.d0)) then 
    Rg = Rg+(CF_DELTA-max(GPP-Rm,0.0d0))*rg_frac
  end if

end subroutine Ra

!------------------------------------------------------------------
subroutine allocate(CF_DELTA, VEG_POOLS, NPP2)

  ! parameters astem
  use obsdrivers
  use parameters
  implicit none
  double precision :: VEG_POOLS(3), NPP2, CF_DELTA

  ! allocate carbon to vegetation pools
  if (decid) VEG_POOLS(1) = VEG_POOLS(1)+CF_DELTA ! leaf
  VEG_POOLS(2) = VEG_POOLS(2)+astem*NPP2          ! stem
  VEG_POOLS(3) = VEG_POOLS(3)+(1.0d0-astem)*NPP2      ! root

end subroutine allocate

!------------------------------------------------------------------
subroutine phenology(GDD, LAI)
  ! parameters gdd_min, gdd_max, laimax, tsmin, leaffall 
  use obsdrivers
  use parameters
  implicit none
  double precision :: GDD, LAI

  ! if spring and GDD requirements met, grow leaves
  if (doy .le. 200) then 
    if (GDD .lt. gdd_min) then 
      LAI = 0.0d0
    else if (GDD .ge. gdd_min .and. GDD .lt. gdd_max) then 
      LAI = laimax*(GDD-gdd_min)/(gdd_max-gdd_min)
    else
      LAI = laimax
    end if
  else
    ! if autumn and cold, drop leves
    if (mint .lt. tsmin .and. LAI .gt. 0) then 
      LAI = LAI - leaffall*laimax
    end if
    if (LAI .lt. 0) LAI = 0.0d0
  end if

end subroutine phenology

!-----------------------------------------------------------------

subroutine litterfall(CF_DELTA, VEG_POOLS, SOIL_POOLS, LITFALL)
  !parameters tleaf, troot, tstem
  use obsdrivers
  use parameters
  implicit none

  double precision :: CF_DELTA, VEG_POOLS(3), LITFALL(2), SOIl_POOLS(2)

  LITFALL(1) = VEG_POOLS(3)*troot
  LITFALL(2) = VEG_POOLS(2)*tstem
  VEG_POOLS(3) = VEG_POOLS(3) - LITFALL(1)
  VEG_POOLS(2) = VEG_POOLS(2) - LITFALL(2)
  if (decid) then 
    if (CF_DELTA .lt. 0) LITFALL(1) = -CF_DELTA
  else
    LITFALL(1) = LITFALL(1) + tleaf*VEG_POOLS(1)
  end if
  SOIL_POOLS(1) = SOIL_POOLS(1)+LITFALL(1)
  SOIL_POOLS(2) = SOIL_POOLS(2)+LITFALL(2)

end subroutine litterfall

!------------------------------------------------------------------
subroutine decomp(SOIL_POOLS, HR)
  !module for computing decomposition
  !parameters q10_hr, br_lit, br_som, dr
  use obsdrivers
  use parameters
  implicit none
  double precision :: litfall(2)
  double precision :: soil_pools(2), HR, D, Trate

  !q10_hr=2.0
  Trate=q10_hr**((0.5d0*(maxt+mint)-10.d0)/10.d0) 
  HR = br_lit*SOIL_POOLS(1)*Trate
  SOIL_POOLS(1) = SOIL_POOLS(1) - br_lit*SOIL_POOLS(1)*Trate
  HR = HR + br_som*SOIL_POOLS(2)*Trate
  SOIL_POOLS(2) = SOIL_POOLS(2) - br_som*SOIL_POOLS(2)*Trate
  D = dr*SOIL_POOLS(1)   !decomposition (litter to SOM)
  SOIL_POOLS(1) = SOIL_POOLS(1)-D
  SOIL_POOLS(2) = SOIL_POOLS(2)+D

end subroutine decomp

!-------------------------------------------------------------------
! Aggregated Canopy Model
!-------------------------------------------------------------------
subroutine Phot(LAI, GPP)
  !parameters lma, nue, leafcn
  USE obsdrivers
  USE parameters
  implicit none

  double precision :: LAI, GPP, NIT 
  double precision :: cps,e0,gs,ci,qq,pp,trange,model_gpp,dec,mult,dayl,pi,a(10)
  pi = 3.14159265358979d0
  trange=0.5*(maxt-mint)

  ! parameter values
  a( 1) =  nue          !nitrogen use efficiency
  a( 2) =  0.0156935d0
  a( 3) =  4.22273d0
  a( 4) =  208.868d0
  a( 5) =  0.0453194d0
  a( 6) =  0.37836d0
  a( 7) =  7.19298d0
  a( 8) =  0.011136d0
  a( 9) =  2.1001d0
  a(10) =  0.789798d0

  Nit = lma/leafcn
  gs = dabs(psid)**a(10)/((a(6)*rtot+trange))
  pp = LAI*Nit/gs*a(1)*dexp(a(8)*maxt)
  qq = a(3)-a(4)

  !internal co2 concentration
  ci = 0.5d0*(Ca+qq-pp+((Ca+qq-pp)**2-4.d0*(Ca*qq-pp*a(3)))**0.5)
  e0 = a(7)*LAI**2/(LAI**2+a(9))

  dec  = -23.4d0*dcos((360.d0*(doy+10.d0)/365.)*pi/180.d0)*pi/180.d0
  mult = dtan(lat)*dtan(dec)
  if (mult.ge.1.) then
    dayl=24.0d0
  else if (mult.le.-1.) then
    dayl=0.d0
  else
    dayl=24.d0*dacos(-mult)/pi
  end if

  cps   = e0*rad*gs*(Ca-ci)/(e0*rad+gs*(Ca-ci))
  ! modified by Xin, model -> model_gpp
  model_gpp = cps*(a(2)*dayl+a(5))
  gpp   = model_gpp

 END subroutine  Phot

!------------------------------------------------------------------


