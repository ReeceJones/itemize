import { AppShell, AppShellHeader, AppShellMain, Box, Group,  Container} from "@mantine/core"
import Header from '@/components/header'

export default function PageContainer({children}: {children: React.ReactNode}) {
  return (
    <AppShell padding="md">
      <AppShellHeader>
        <Header/>
      </AppShellHeader>
      <AppShellMain pt={100}>
        <Container>
          {children}
        </Container>
      </AppShellMain>
    </AppShell>
  )
}